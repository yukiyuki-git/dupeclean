"""File deduplication cleanup strategy module for DupeClean.

Manage cleanup strategies for different scenarios.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class CleanupStrategyConfig:
    """Configuration for a cleanup strategy."""

    name: str
    description: str
    keep_rule: str  # "shortest", "newest", "oldest", "first"
    action: str = "hardlink"  # "hardlink", "delete", "move"
    min_file_size: int = 0
    max_file_size: int = 0
    extensions: list[str] = field(default_factory=list)

    def matches_file(self, fi: FileInfo) -> bool:
        """Check if a file matches this strategy's filters."""
        if self.min_file_size > 0 and fi.size < self.min_file_size:
            return False
        if self.max_file_size > 0 and fi.size > self.max_file_size:
            return False
        return not (self.extensions and fi.ext.lower() not in self.extensions)


# Built-in strategies
BUILTIN_STRATEGIES = {
    "default": CleanupStrategyConfig(
        name="Default",
        description="Keep shortest path, hardlink duplicates",
        keep_rule="shortest",
        action="hardlink",
    ),
    "aggressive": CleanupStrategyConfig(
        name="Aggressive",
        description="Delete all duplicates, keep newest",
        keep_rule="newest",
        action="delete",
    ),
    "conservative": CleanupStrategyConfig(
        name="Conservative",
        description="Hardlink only large files",
        keep_rule="shortest",
        action="hardlink",
        min_file_size=10240,  # 10KB
    ),
    "media": CleanupStrategyConfig(
        name="Media",
        description="Dedup media files only",
        keep_rule="newest",
        action="hardlink",
        extensions=[".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3"],
    ),
}


def get_strategy(name: str) -> CleanupStrategyConfig:
    """Get a strategy by name."""
    return BUILTIN_STRATEGIES.get(name, BUILTIN_STRATEGIES["default"])


def list_strategies() -> list[CleanupStrategyConfig]:
    """List all available strategies."""
    return list(BUILTIN_STRATEGIES.values())


def format_strategy(strategy: CleanupStrategyConfig) -> str:
    """Format strategy as text."""
    lines = [
        f"Strategy: {strategy.name}",
        f"  Description: {strategy.description}",
        f"  Keep rule: {strategy.keep_rule}",
        f"  Action: {strategy.action}",
    ]
    if strategy.min_file_size > 0:
        lines.append(f"  Min size: {format_size(strategy.min_file_size)}")
    if strategy.max_file_size > 0:
        lines.append(f"  Max size: {format_size(strategy.max_file_size)}")
    if strategy.extensions:
        lines.append(f"  Extensions: {', '.join(strategy.extensions)}")
    return "\n".join(lines)
