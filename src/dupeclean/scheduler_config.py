"""File deduplication cleanup scheduler config for DupeClean.

Configuration for cleanup scheduler.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SchedulerConfig:
    """Configuration for cleanup scheduler."""

    max_concurrent: int = 1
    retry_count: int = 3
    retry_delay: float = 60.0
    timeout: float = 3600.0
    log_path: Path | None = None
    enabled: bool = True

    def to_dict(self) -> dict:
        return {
            "max_concurrent": self.max_concurrent,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
            "log_path": str(self.log_path) if self.log_path else None,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SchedulerConfig:
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


def create_default_config() -> SchedulerConfig:
    """Create default scheduler configuration."""
    return SchedulerConfig()


def create_fast_config() -> SchedulerConfig:
    """Create fast scheduler configuration."""
    return SchedulerConfig(
        max_concurrent=4,
        retry_count=1,
        retry_delay=10.0,
        timeout=600.0,
    )


def format_config(config: SchedulerConfig) -> str:
    """Format config as text."""
    return (
        f"Scheduler Config:\n"
        f"  Max concurrent: {config.max_concurrent}\n"
        f"  Retry count: {config.retry_count}\n"
        f"  Retry delay: {config.retry_delay}s\n"
        f"  Timeout: {config.timeout}s\n"
        f"  Enabled: {config.enabled}"
    )
