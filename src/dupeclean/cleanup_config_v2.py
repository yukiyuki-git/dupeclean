"""File deduplication cleanup config v2 for DupeClean.

Enhanced cleanup configuration with presets.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CleanupConfigV2:
    """Enhanced cleanup configuration."""

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
    max_depth: int = 50
    threads: int = 4
    verbose: bool = False

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
            "max_depth": self.max_depth,
            "threads": self.threads,
            "verbose": self.verbose,
        }

    @classmethod
    def from_dict(cls, data: dict) -> CleanupConfigV2:
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


def create_fast_cleanup_config() -> CleanupConfigV2:
    """Create fast cleanup configuration."""
    return CleanupConfigV2(
        strategy="shortest",
        action="hardlink",
        verify=False,
        backup=False,
        threads=8,
    )


def create_safe_cleanup_config() -> CleanupConfigV2:
    """Create safe cleanup configuration."""
    return CleanupConfigV2(
        strategy="shortest",
        action="hardlink",
        verify=True,
        backup=True,
        dry_run=True,
        max_errors=10,
    )


def format_cleanup_config_v2(config: CleanupConfigV2) -> str:
    """Format config as text."""
    return (
        f"Cleanup Config:\n"
        f"  Strategy: {config.strategy}\n"
        f"  Action: {config.action}\n"
        f"  Dry run: {config.dry_run}\n"
        f"  Verify: {config.verify}\n"
        f"  Backup: {config.backup}\n"
        f"  Threads: {config.threads}\n"
        f"  Max depth: {config.max_depth}"
    )
