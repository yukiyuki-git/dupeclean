"""File deduplication cleanup config module for DupeClean.

Configuration for cleanup operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CleanupConfig:
    """Configuration for cleanup operations."""

    strategy: str = "shortest"
    action: str = "hardlink"
    dry_run: bool = True
    verify: bool = True
    backup: bool = True
    max_errors: int = 100
    timeout: float = 3600.0
    min_file_size: int = 0
    max_file_size: int = 0
    extensions: list[str] = field(default_factory=list)
    ignore_patterns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy,
            "action": self.action,
            "dry_run": self.dry_run,
            "verify": self.verify,
            "backup": self.backup,
            "max_errors": self.max_errors,
            "timeout": self.timeout,
            "min_file_size": self.min_file_size,
            "max_file_size": self.max_file_size,
            "extensions": self.extensions,
            "ignore_patterns": self.ignore_patterns,
        }

    @classmethod
    def from_dict(cls, data: dict) -> CleanupConfig:
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


def create_default_cleanup_config() -> CleanupConfig:
    """Create default cleanup configuration."""
    return CleanupConfig()


def create_aggressive_config() -> CleanupConfig:
    """Create aggressive cleanup configuration."""
    return CleanupConfig(
        strategy="newest",
        action="delete",
        verify=False,
        backup=False,
    )


def create_safe_config() -> CleanupConfig:
    """Create safe cleanup configuration."""
    return CleanupConfig(
        strategy="shortest",
        action="hardlink",
        verify=True,
        backup=True,
        dry_run=True,
    )


def format_cleanup_config(config: CleanupConfig) -> str:
    """Format config as text."""
    return (
        f"Cleanup Config:\n"
        f"  Strategy: {config.strategy}\n"
        f"  Action: {config.action}\n"
        f"  Dry run: {config.dry_run}\n"
        f"  Verify: {config.verify}\n"
        f"  Backup: {config.backup}"
    )
