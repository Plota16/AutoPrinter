from watchdog.events import FileSystemEventHandler

from src.auto_printer.logger import logger


class DirectoryWatcherEventHandler(FileSystemEventHandler):
    """Handles file system events"""

    def __init__(self, printer):
        self.printer = printer

    def on_created(self, event):
        """Called when a file or directory is created"""
        if not event.is_directory:
            logger.info(f"✓ File created: {event.src_path}")
            self.printer.print_file(event.src_path)
        else:
            logger.debug(f"✓ Directory created: {event.src_path}")

    def on_modified(self, event):
        """Called when a file or directory is modified"""
        if not event.is_directory:
            logger.debug(f"✎ File modified: {event.src_path}")

    def on_deleted(self, event):
        """Called when a file or directory is deleted"""
        if not event.is_directory:
            logger.debug(f"✗ File deleted: {event.src_path}")
        else:
            logger.debug(f"✗ Directory deleted: {event.src_path}")

    def on_moved(self, event):
        """Called when a file or directory is moved or renamed"""
        if not event.is_directory:
            logger.debug(f"➜ File moved: {event.src_path} → {event.dest_path}")
        else:
            logger.debug(f"➜ Directory moved: {event.src_path} → {event.dest_path}")