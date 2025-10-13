from src.auto_printer.arg_parser import ArgumentParser
from src.auto_printer.file_watcher.directory_watcher import DirectoryWatcher
from src.auto_printer.file_watcher.event_handler import DirectoryWatcherEventHandler
from src.auto_printer.logger import setup_logger
from src.auto_printer.printer import Printer
from src.auto_printer.settings import WatcherSettings

def main():
    """Main entry point for the application"""
    # Parse arguments
    args = ArgumentParser.parse()

    # Setup settings
    settings = WatcherSettings()
    settings.watch_path = args.watch
    settings.printer_name = args.printer


    # Setup dependencies
    printer = Printer(settings)
    handler = DirectoryWatcherEventHandler(printer)
    watcher = DirectoryWatcher(settings, handler)

    # Start watching
    watcher.watch_directory()


if __name__ == "__main__":
    main()