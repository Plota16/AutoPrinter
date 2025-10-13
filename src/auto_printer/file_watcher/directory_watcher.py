"""
Directory Watcher - Monitors a directory for file system changes

Installation:
    pip install watchdog pydantic-settings
"""

import time
from watchdog.observers import Observer
import os

from src.auto_printer.file_watcher.event_handler import DirectoryWatcherEventHandler
from src.auto_printer.settings import WatcherSettings
from src.auto_printer.logger import logger


class DirectoryWatcher:

    def __init__(self, settings: WatcherSettings, handler: DirectoryWatcherEventHandler):
        self.path = settings.watch_path
        self.handler = handler
        self.sleep_time = settings.sleep_interval

    def watch_directory(self):
        """
        Watch a directory for changes
        """
        # Validate path
        if not os.path.exists(self.path):
            logger.warning(f"Error: Path '{self.path}' does not exist")
            raise Exception(f"Path '{self.path}' does not exist")

        if not os.path.isdir(self.path):
            logger.warning(f"Error: '{self.path}' is not a directory")
            raise Exception(f"Error '{self.path}' is not a directory")

        observer = Observer()
        observer.schedule(self.handler, self.path, recursive=True)

        # Start watching
        observer.start()
        logger.info(f"👁 Watching directory: {self.path}")
        logger.info(f"Check interval: {self.sleep_time}s")
        logger.info("Press Ctrl+C to stop\n")

        try:
            while True:
                time.sleep(self.sleep_time)
        except KeyboardInterrupt:
            observer.stop()
            logger.warning("\n\nStopped watching directory")

        observer.join()
