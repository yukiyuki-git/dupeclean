"""File deduplication cleanup module for DupeClean.

Execute cleanup operations from dedup results.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import CleanupAction, DuplicateGroup, format_size
from .utils import create_hardlink, safe_remove


@dataclass
class CleanupStats:
    """Statistics from a cleanup operation."""

    files_processed: int = 0
    files_deleted: int = 0
    hardlinks_created: int = 0
    space_freed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return self.files_deleted + self.hardlinks_created

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)


def cleanup_duplicates(
    groups: list[DuplicateGroup],
    action: CleanupAction = CleanupAction.HARDLINK,
    dry_run: bool = True,
) -> CleanupStats:
    """Execute cleanup on duplicate groups.

    Args:
        groups: Duplicate groups to clean.
        action: Cleanup action (hardlink/delete).
        dry_run: If True, don't modify files.

    Returns:
        CleanupStats with operation results.
    """
    stats = CleanupStats()

    for group in groups:
        if len(group.files) < 2:
            continue

        keeper = group.files[0]  # Keep first file
        for dupe in group.files[1:]:
            stats.files_processed += 1

            if dry_run:
                stats.files_deleted += 1
                stats.space_freed += dupe.size
                continue

            if action == CleanupAction.DELETE:
                success, error = safe_remove(dupe.path)
                if success:
                    stats.files_deleted += 1
                    stats.space_freed += dupe.size
                elif error:
                    stats.errors.append(error)

            elif action == CleanupAction.HARDLINK:
                success, error = create_hardlink(keeper.path, dupe.path)
                if success:
                    stats.hardlinks_created += 1
                    stats.space_freed += dupe.size
                elif error:
                    stats.errors.append(error)

    return stats


def format_cleanup_stats(stats: CleanupStats) -> str:
    """Format cleanup stats as text."""
    lines = [
        "Cleanup Results:",
        f"  Processed: {stats.files_processed:,}",
        f"  Deleted: {stats.files_deleted:,}",
        f"  Hardlinked: {stats.hardlinks_created:,}",
        f"  Space freed: {stats.freed_display}",
    ]

    if stats.errors:
        lines.append(f"\n  Errors ({len(stats.errors)}):")
        for err in stats.errors[:10]:
            lines.append(f"    {err}")

    return "\n".join(lines)
