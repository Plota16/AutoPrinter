import argparse

from src.auto_printer.logger import logger


class ArgumentParser:

    def __init__(self):
        pass

    @staticmethod
    def parse():
        parser = argparse.ArgumentParser(
            description="Watch a directory for file system changes and auto-print"
        )
        parser.add_argument(
            "--watch",
            required=True,
            help="Path to the directory to watch"
        )
        parser.add_argument(
            "--printer",
            required=False,
            default=None,
            help="Name of the printer to use (default: system default printer)"
        )

        args = parser.parse_args()
        logger.debug(f"ARGS: {args}")

        return args
