import os
from time import sleep

import win32api
import win32print

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

    import os
    import time

    def print_file(self, file_path, printer_name=None):
        """
        Print a file to a Windows printer (printer is preconfigured to A4).

        Args:
            file_path: Path to the file to print
            printer_name: Optional printer override
        """
        if self.printer is None:
            logger.warning("No printer found")
            raise RuntimeError("No printer found")

        target_printer = printer_name or self.printer

        # Check if printer is online before printing
        # if not self._is_printer_online(target_printer):
        #     logger.warning(f"Printer '{target_printer}' is offline or not ready.")
        #     raise RuntimeError(f"Printer '{target_printer}' is offline or not ready.")

        # Wait for file to be fully written and accessible
        max_retries = 10
        retry_delay = 0.5  # seconds

        for attempt in range(max_retries):
            if os.path.exists(file_path):
                try:
                    # Try to open the file to ensure it's not locked
                    with open(file_path, 'rb') as f:
                        f.read(1)
                    break
                except (IOError, PermissionError):
                    if attempt < max_retries - 1:
                        sleep(retry_delay)
                    else:
                        raise RuntimeError(f"File '{file_path}' is locked or inaccessible")
            else:
                if attempt < max_retries - 1:
                    sleep(retry_delay)
                else:
                    raise FileNotFoundError(f"File '{file_path}' does not exist")

        # Additional small delay to ensure file is fully written
        sleep(0.2)

        # Convert to absolute path
        abs_file_path = os.path.abspath(file_path)

        # Print the file
        win32api.ShellExecute(
            0,
            "print",
            abs_file_path,
            f'/d:"{target_printer}"',
            ".",
            0
        )
        logger.info(f"✓ Sent '{abs_file_path}' to printer: {target_printer} (A4 format)")
