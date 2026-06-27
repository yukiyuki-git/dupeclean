"""File deduplication scan config module for DupeClean.

Configuration for scan operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScanConfig:
    """Configuration for scan operations."""

    follow_symlinks: bool = False
    skip_hidden: bool = True
    max_depth: int = 50
    threads: int = 4
    ignore_patterns: list[str] = field(
        default_factory=lambda: [
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
        ]
    )
    min_file_size: int = 0
    max_file_size: int = 0
    extensions: list[str] = field(default_factory=list)

    def should_ignore(self, name: str) -> bool:
        """Check if a name matches any ignore pattern."""
        return any(name == p or name.startswith(".") for p in self.ignore_patterns)

    def should_skip_size(self, size: int) -> bool:
        """Check if a file size should be skipped."""
        if self.min_file_size > 0 and size < self.min_file_size:
            return True
        return self.max_file_size > 0 and size > self.max_file_size

    def should_skip_extension(self, ext: str) -> bool:
        """Check if an extension should be skipped."""
        if not self.extensions:
            return False
        return ext.lower() not in {e.lower() for e in self.extensions}

    def to_dict(self) -> dict:
        return {
            "follow_symlinks": self.follow_symlinks,
            "skip_hidden": self.skip_hidden,
            "max_depth": self.max_depth,
            "threads": self.threads,
            "ignore_patterns": self.ignore_patterns,
            "min_file_size": self.min_file_size,
            "max_file_size": self.max_file_size,
            "extensions": self.extensions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScanConfig:
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


def create_fast_scan_config() -> ScanConfig:
    """Create fast scan configuration."""
    return ScanConfig(
        threads=8,
        max_depth=10,
        skip_hidden=True,
    )


def create_thorough_scan_config() -> ScanConfig:
    """Create thorough scan configuration."""
    return ScanConfig(
        threads=4,
        max_depth=100,
        skip_hidden=False,
        follow_symlinks=False,
    )


def format_scan_config(config: ScanConfig) -> str:
    """Format scan config as text."""
    return (
        f"Scan Config:\n"
        f"  Threads: {config.threads}\n"
        f"  Max depth: {config.max_depth}\n"
        f"  Follow symlinks: {config.follow_symlinks}\n"
        f"  Skip hidden: {config.skip_hidden}\n"
        f"  Ignore: {', '.join(config.ignore_patterns[:5])}..."
    )
