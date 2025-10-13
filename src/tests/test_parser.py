import unittest
from unittest import mock

from src.auto_printer.arg_parser import ArgumentParser


class TestArgumentParser(unittest.TestCase):

    @mock.patch("argparse.ArgumentParser.parse_args")
    def test_parse_with_required_argument(self, mock_parse_args):
        # Mock the parsed arguments
        mock_parse_args.return_value = mock.Mock(watch="/path/to/dir", printer="MyPrinter")

        # Call the parse method
        args = ArgumentParser.parse()

        # Assertions
        self.assertEqual(args.watch, "/path/to/dir")
        self.assertEqual(args.printer, "MyPrinter")

    @mock.patch("argparse.ArgumentParser.parse_args")
    def test_parse_with_default_printer(self, mock_parse_args):
        # Mock only the required argument
        mock_parse_args.return_value = mock.Mock(watch="/path/to/dir", printer=None)

        args = ArgumentParser.parse()

        self.assertEqual(args.watch, "/path/to/dir")
        self.assertIsNone(args.printer)


if __name__ == "__main__":
    unittest.main()
