"""File deduplication cleanup context module for DupeClean.

Manage cleanup operation context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class CleanupContext:
    """Context for a cleanup operation."""

    root: Path
    groups: list[DuplicateGroup] = field(default_factory=list)
    files: list[FileInfo] = field(default_factory=list)
    strategy: str = "shortest"
    dry_run: bool = True
    metadata: dict = field(default_factory=dict)

    @property
    def total_groups(self) -> int:
        return len(self.groups)

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_duplicates(self) -> int:
        return sum(g.count for g in self.groups)

    @property
    def total_wasted(self) -> int:
        return sum(g.wasted_space for g in self.groups)

    def get_group(self, group_id: int) -> DuplicateGroup | None:
        """Get a group by ID."""
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None


def create_context(
    root: Path,
    files: list[FileInfo],
    groups: list[DuplicateGroup],
    strategy: str = "shortest",
    dry_run: bool = True,
) -> CleanupContext:
    """Create a cleanup context."""
    return CleanupContext(
        root=root,
        groups=groups,
        files=files,
        strategy=strategy,
        dry_run=dry_run,
    )


def format_context(context: CleanupContext) -> str:
    """Format context as text."""
    mode = "DRY RUN" if context.dry_run else "LIVE"
    return (
        f"Cleanup Context:\n"
        f"  Root: {context.root}\n"
        f"  Strategy: {context.strategy}\n"
        f"  Mode: {mode}\n"
        f"  Files: {context.total_files:,}\n"
        f"  Groups: {context.total_groups:,}\n"
        f"  Duplicates: {context.total_duplicates:,}\n"
        f"  Wasted: {format_size(context.total_wasted)}"
    )
