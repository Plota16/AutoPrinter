from pydantic_settings import BaseSettings


class WatcherSettings(BaseSettings):
    """Configuration settings for directory watcher"""
    sleep_interval: float = 1.0  # seconds between checks
    watch_path: str = "."  # directory to watch
    printer_name: str = ""

    class Config:
        case_sensitive = False