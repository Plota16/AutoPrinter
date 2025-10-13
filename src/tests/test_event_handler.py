import pytest
from unittest.mock import Mock, patch
from watchdog.events import (
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    FileMovedEvent,
    DirCreatedEvent,
    DirModifiedEvent,
    DirDeletedEvent,
    DirMovedEvent,
)

from src.auto_printer.file_watcher.event_handler import DirectoryWatcherEventHandler


class TestDirectoryWatcherEventHandler:
    """Test suite for DirectoryWatcherEventHandler"""

    @pytest.fixture
    def handler(self):
        """Create a handler instance for each test"""
        return DirectoryWatcherEventHandler()

    # Test on_created
    @patch("builtins.print")
    def test_on_created_file(self, mock_print, handler):
        """Test that file creation prints the correct message"""
        event = FileCreatedEvent("/path/to/file.txt")
        handler.on_created(event)
        mock_print.assert_called_once_with("✓ File created: /path/to/file.txt")

    @patch("builtins.print")
    def test_on_created_directory(self, mock_print, handler):
        """Test that directory creation prints the correct message"""
        event = DirCreatedEvent("/path/to/directory")
        handler.on_created(event)
        mock_print.assert_called_once_with("✓ Directory created: /path/to/directory")

    # Test on_modified
    @patch("builtins.print")
    def test_on_modified_file(self, mock_print, handler):
        """Test that file modification prints the correct message"""
        event = FileModifiedEvent("/path/to/file.txt")
        handler.on_modified(event)
        mock_print.assert_called_once_with("✎ File modified: /path/to/file.txt")

    @patch("builtins.print")
    def test_on_modified_directory(self, mock_print, handler):
        """Test that directory modification doesn't print anything"""
        event = DirModifiedEvent("/path/to/directory")
        handler.on_modified(event)
        mock_print.assert_not_called()

    # Test on_deleted
    @patch("builtins.print")
    def test_on_deleted_file(self, mock_print, handler):
        """Test that file deletion prints the correct message"""
        event = FileDeletedEvent("/path/to/file.txt")
        handler.on_deleted(event)
        mock_print.assert_called_once_with("✗ File deleted: /path/to/file.txt")

    @patch("builtins.print")
    def test_on_deleted_directory(self, mock_print, handler):
        """Test that directory deletion prints the correct message"""
        event = DirDeletedEvent("/path/to/directory")
        handler.on_deleted(event)
        mock_print.assert_called_once_with("✗ Directory deleted: /path/to/directory")

    # Test on_moved
    @patch("builtins.print")
    def test_on_moved_file(self, mock_print, handler):
        """Test that file move/rename prints the correct message"""
        event = FileMovedEvent("/path/to/old.txt", "/path/to/new.txt")
        handler.on_moved(event)
        mock_print.assert_called_once_with(
            "➜ File moved: /path/to/old.txt → /path/to/new.txt"
        )

    @patch("builtins.print")
    def test_on_moved_directory(self, mock_print, handler):
        """Test that directory move/rename prints the correct message"""
        event = DirMovedEvent("/path/to/old_dir", "/path/to/new_dir")
        handler.on_moved(event)
        mock_print.assert_called_once_with(
            "➜ Directory moved: /path/to/old_dir → /path/to/new_dir"
        )

    # Test with different path formats
    @patch("builtins.print")
    def test_handles_various_path_formats(self, mock_print, handler):
        """Test that handler works with different path formats"""
        paths = [
            "/absolute/path/file.txt",
            "relative/path/file.txt",
            "../parent/file.txt",
            "./current/file.txt",
        ]

        for path in paths:
            event = FileCreatedEvent(path)
            handler.on_created(event)
            mock_print.assert_called_with(f"✓ File created: {path}")
            mock_print.reset_mock()

    # Test inheritance
    def test_inherits_from_file_system_event_handler(self, handler):
        """Test that handler inherits from FileSystemEventHandler"""
        from watchdog.events import FileSystemEventHandler
        assert isinstance(handler, FileSystemEventHandler)

    # Integration-style test
    @patch("builtins.print")
    def test_multiple_events_sequence(self, mock_print, handler):
        """Test a sequence of multiple events"""
        # Create file
        handler.on_created(FileCreatedEvent("/tmp/test.txt"))
        # Modify file
        handler.on_modified(FileModifiedEvent("/tmp/test.txt"))
        # Move file
        handler.on_moved(FileMovedEvent("/tmp/test.txt", "/tmp/test_renamed.txt"))
        # Delete file
        handler.on_deleted(FileDeletedEvent("/tmp/test_renamed.txt"))

        assert mock_print.call_count == 4
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert "✓ File created: /tmp/test.txt" in calls
        assert "✎ File modified: /tmp/test.txt" in calls
        assert "➜ File moved: /tmp/test.txt → /tmp/test_renamed.txt" in calls
        assert "✗ File deleted: /tmp/test_renamed.txt" in calls