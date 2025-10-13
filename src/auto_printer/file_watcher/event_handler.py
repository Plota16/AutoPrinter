import os
import time
from watchdog.events import FileSystemEventHandler

from src.auto_printer.logger import logger


class DirectoryWatcherEventHandler(FileSystemEventHandler):
    """Handles file system events"""

    def __init__(self, printer):
        self.printer = printer
        self.processed_files = {}  # Track files and their last modification time
        self.debounce_seconds = 5  # Don't print the same file within 5 seconds

    def _should_process(self, file_path):
        """Check if this file should be processed (not recently printed)."""
        current_time = time.time()

        # Get file modification time to detect if it's actually a different version
        try:
            file_mtime = os.path.getmtime(file_path)
        except OSError:
            return False  # File doesn't exist or can't be accessed

        # Check if we've recently processed this file
        if file_path in self.processed_files:
            last_processed_time, last_mtime = self.processed_files[file_path]

            # If the file hasn't changed and we processed it recently, skip
            time_since_last = current_time - last_processed_time
            if time_since_last < self.debounce_seconds and file_mtime == last_mtime:
                logger.debug(f"⏭️ Skipping duplicate print event for: {os.path.basename(file_path)}")
                return False

        # Update tracking
        self.processed_files[file_path] = (current_time, file_mtime)

        # Clean up old entries (keep only last hour)
        cutoff_time = current_time - 3600
        self.processed_files = {
            k: v for k, v in self.processed_files.items()
            if v[0] > cutoff_time
        }

        return True

    def on_created(self, event):
        """Called when a file or directory is created"""
        if not event.is_directory:
            if not event.src_path.lower().endswith('.pdf'):
                logger.debug(f"✓ Non-PDF file created (ignored): {event.src_path}")
                return

            logger.info(f"✓ File created: {event.src_path}")

            if not self._should_process(event.src_path):
                return

            try:
                self.printer.print_file(event.src_path)
                self.processed_files.clear()
            except Exception as e:
                logger.error(f"Failed to print {event.src_path}: {e}")
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