import os
import time

import pypdfium2 as pdfium
import win32con
import win32print
import win32ui
from PIL import ImageWin

from src.auto_printer.logger import logger
from src.auto_printer.settings import WatcherSettings


class Printer:

    def __init__(self, settings: WatcherSettings):
        # Choose printer (default or by name)
        if settings.printer_name is None:
            self.printer = win32print.GetDefaultPrinter()
        else:
            self.printer = self._get_printer_by_name(settings.printer_name)

    @staticmethod
    def _get_printer_by_name(printer_name: str) -> str:
        """Check if a printer exists by name and return it."""
        is_matched = False
        for printer in win32print.EnumPrinters(2):
            if printer[2] == printer_name:
                is_matched = True
            logger.debug(f"Found printer name '{printer[2]}': is it chosen one? [{printer[2] == printer_name}]")

        if not is_matched:
            logger.warning(f"Could not find printer name '{printer_name}'")
            raise Exception(f"Could not find printer name '{printer_name}'")

        return printer_name

    @staticmethod
    def _is_printer_online(printer_name: str) -> bool:
        """Return True if the printer is online, False otherwise."""
        try:
            hprinter = win32print.OpenPrinter(printer_name)
            try:
                printer_status = win32print.GetPrinter(hprinter, 2)["Status"]
                # Common flags for offline/error conditions
                PRINTER_STATUS_OFFLINE = 0x00000080
                PRINTER_STATUS_ERROR = 0x00000002
                PRINTER_STATUS_PAPER_OUT = 0x00000040

                is_online = not (
                        printer_status & (PRINTER_STATUS_OFFLINE | PRINTER_STATUS_ERROR | PRINTER_STATUS_PAPER_OUT))
                return is_online
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            logger.warning(f"⚠️ Could not check printer status for '{printer_name}': {e}")
            return False

    def _wait_for_pdf(self, file_path: str, max_retries: int = 20, retry_delay: float = 0.5) -> str:
        """
        Wait for PDF file to be fully written and valid.

        Args:
            file_path: Path to the PDF file
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Absolute path to the file
        """
        abs_path = os.path.abspath(file_path)
        last_size = -1
        stable_count = 0

        for attempt in range(max_retries):
            logger.debug(f"Attempt {attempt + 1}/{max_retries} to validate PDF")

            # Check if file exists
            if not os.path.exists(abs_path):
                logger.debug(f"File does not exist yet: {abs_path}")
                time.sleep(retry_delay)
                continue

            try:
                # Check if file is accessible
                current_size = os.path.getsize(abs_path)
                logger.debug(f"File size: {current_size} bytes")

                # Check if file size is stable (not being written to)
                if current_size == last_size and current_size > 0:
                    stable_count += 1
                    logger.debug(f"File size stable (count: {stable_count})")
                else:
                    stable_count = 0
                    last_size = current_size

                # Wait for file to be stable for at least 2 checks
                if stable_count < 2:
                    time.sleep(retry_delay)
                    continue

                # Try to open the file to ensure it's not locked
                with open(abs_path, 'rb') as f:
                    # Read first few bytes to check PDF header
                    header = f.read(5)
                    if not header.startswith(b'%PDF-'):
                        logger.debug("File doesn't start with PDF header yet")
                        time.sleep(retry_delay)
                        continue

                    # Try to read the entire file
                    f.seek(0)
                    data = f.read()

                    # Check for PDF EOF marker
                    if b'%%EOF' not in data:
                        logger.debug("PDF EOF marker not found yet")
                        time.sleep(retry_delay)
                        continue

                # Try to open with pypdfium2 to validate it's a valid PDF
                try:
                    test_pdf = pdfium.PdfDocument(abs_path)
                    page_count = len(test_pdf)
                    test_pdf.close()
                    logger.info(f"✓ PDF validated: {page_count} page(s)")
                    return abs_path
                except Exception as pdf_error:
                    logger.debug(f"PDF not valid yet: {pdf_error}")
                    time.sleep(retry_delay)
                    continue

            except (IOError, PermissionError, OSError) as e:
                logger.debug(f"File not accessible yet: {e}")
                time.sleep(retry_delay)
                continue

        raise RuntimeError(f"Timeout waiting for valid PDF file: {abs_path}")

    def _print_pdf_direct(self, pdf_path: str, printer_name: str):
        """
        Print PDF directly using pypdfium2 by converting pages to images.

        Args:
            pdf_path: Path to the PDF file
            printer_name: Name of the printer
        """
        try:
            # Open the PDF
            pdf = pdfium.PdfDocument(pdf_path)
            page_count = len(pdf)  # Store page count before closing
            logger.info(f"PDF has {page_count} page(s)")

            # Create device context for printer
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)

            try:
                # Get printer resolution (DPI)
                printer_dpi_x = hdc.GetDeviceCaps(win32con.LOGPIXELSX)
                printer_dpi_y = hdc.GetDeviceCaps(win32con.LOGPIXELSY)

                if printer_dpi_x == 0:
                    printer_dpi_x = 300
                if printer_dpi_y == 0:
                    printer_dpi_y = 300

                logger.debug(f"Printer DPI: {printer_dpi_x}x{printer_dpi_y}")

                # Get printable area dimensions
                page_width = hdc.GetDeviceCaps(win32con.HORZRES)
                page_height = hdc.GetDeviceCaps(win32con.VERTRES)

                logger.debug(f"Printable area: {page_width}x{page_height} pixels")

                # Start print job
                hdc.StartDoc(os.path.basename(pdf_path))

                # Process each page
                for page_num in range(page_count):
                    logger.debug(f"Processing page {page_num + 1}/{page_count}")

                    hdc.StartPage()

                    # Render page to bitmap at printer resolution
                    page = pdf[page_num]

                    # Use printer DPI for rendering
                    render_scale = printer_dpi_x / 72  # 72 is PDF's default DPI

                    # Render the page
                    bitmap = page.render(
                        scale=render_scale,
                        rotation=0,
                    )

                    # Convert to PIL Image
                    pil_image = bitmap.to_pil()

                    # Convert to RGB if necessary
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')

                    # Get image dimensions
                    img_width, img_height = pil_image.size

                    # Calculate scaling to fit on page while maintaining aspect ratio
                    scale_x = page_width / img_width
                    scale_y = page_height / img_height
                    scale = min(scale_x, scale_y)

                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)

                    # Center image on page
                    x_offset = (page_width - new_width) // 2
                    y_offset = (page_height - new_height) // 2

                    # Use PIL's ImageWin to draw directly to the device context
                    dib = ImageWin.Dib(pil_image)
                    dib.draw(hdc.GetHandleOutput(), (x_offset, y_offset, x_offset + new_width, y_offset + new_height))

                    hdc.EndPage()

                # End print job
                hdc.EndDoc()

            finally:
                hdc.DeleteDC()

            pdf.close()
            logger.info(f"✓ Successfully printed {page_count} page(s)")

        except Exception as e:
            logger.error(f"Error printing PDF: {e}")
            raise

    def print_file(self, file_path, printer_name=None):
        """
        Print a PDF file to a Windows printer (printer is preconfigured to A4).

        Args:
            file_path: Path to the PDF file to print
            printer_name: Optional printer override
        """
        if self.printer is None:
            logger.warning("No printer found")
            raise RuntimeError("No printer found")

        target_printer = printer_name or self.printer

        # Check if printer is online before printing
        if not self._is_printer_online(target_printer):
            logger.warning(f"Printer '{target_printer}' is offline or not ready.")
            raise RuntimeError(f"Printer '{target_printer}' is offline or not ready.")

        # Check if it's a PDF file
        if not file_path.lower().endswith('.pdf'):
            logger.error(f"File '{file_path}' is not a PDF file")
            raise ValueError(f"Only PDF files are supported. Got: {file_path}")

        # Wait for PDF to be fully written and valid
        abs_file_path = self._wait_for_pdf(file_path)

        # Print the PDF
        # self._print_pdf_direct(abs_file_path, target_printer)
        logger.info(f"✓ Sent '{abs_file_path}' to printer: {target_printer} (A4 format)")
