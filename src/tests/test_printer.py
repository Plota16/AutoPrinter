import unittest
from unittest.mock import patch, MagicMock
from src.auto_printer.printer import Printer
from src.auto_printer.settings import WatcherSettings


class TestPrinter(unittest.TestCase):

    @patch("src.auto_printer.printer.win32print.GetDefaultPrinter", return_value="DefaultPrinter")
    def test_init_with_no_printer_name(self, mock_get_default):
        settings = WatcherSettings()
        settings.printer_name = None
        printer = Printer(settings)
        self.assertEqual(printer.printer, "DefaultPrinter")
        mock_get_default.assert_called_once()

    @patch("src.auto_printer.printer.win32print.EnumPrinters")
    def test_get_printer_by_name_found(self, mock_enum):
        # Mock available printers list
        mock_enum.return_value = [
            (None, None, "PrinterA", None),
            (None, None, "PrinterB", None),
        ]
        result = Printer._get_printer_by_name("PrinterB")
        self.assertTrue(result)

    @patch("src.auto_printer.printer.win32print.EnumPrinters")
    def test_get_printer_by_name_not_found_raises(self, mock_enum):
        mock_enum.return_value = [
            (None, None, "PrinterA", None),
        ]
        with self.assertRaises(Exception) as context:
            Printer._get_printer_by_name("PrinterZ")
        self.assertIn("Could not find printer name 'PrinterZ'", str(context.exception))

    @patch("src.auto_printer.printer.win32api.ShellExecute")
    def test_print_file_calls_shell_execute(self, mock_shell):
        settings = WatcherSettings(printer_name="MyPrinter")

        with patch.object(Printer, "_get_printer_by_name", return_value=True):
            printer = Printer(settings)

        printer.print_file("file.pdf", printer_name="MyPrinter")

        mock_shell.assert_called_once_with(
            0, "print", "file.pdf", '/d:"MyPrinter"', ".", 0
        )

    def test_print_file_raises_if_no_printer(self):
        settings = WatcherSettings(printer_name="SomePrinter")
        printer = Printer.__new__(Printer)  # bypass __init__
        printer.printer = None  # simulate missing printer

        with self.assertRaises(RuntimeError):
            printer.print_file("file.pdf")


if __name__ == "__main__":
    unittest.main()
