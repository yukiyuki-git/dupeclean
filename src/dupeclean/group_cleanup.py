"""File deduplication duplicate group cleanup for DupeClean.

Clean up duplicate groups by applying selected actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size
from .utils import create_hardlink, safe_remove


@dataclass
class GroupCleanupResult:
    """Result of cleaning up a group."""

    group_id: int
    files_removed: int = 0
    hardlinks_created: int = 0
    space_freed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)


@dataclass
class BatchCleanupResult:
    """Result of batch group cleanup."""

    results: list[GroupCleanupResult] = field(default_factory=list)

    @property
    def total_groups(self) -> int:
        return len(self.results)

    @property
    def total_removed(self) -> int:
        return sum(r.files_removed for r in self.results)

    @property
    def total_freed(self) -> int:
        return sum(r.space_freed for r in self.results)

    @property
    def total_errors(self) -> int:
        return sum(len(r.errors) for r in self.results)


def cleanup_group_delete(
    group: DuplicateGroup,
    keep_idx: int = 0,
    dry_run: bool = True,
) -> GroupCleanupResult:
    """Clean up a group by deleting duplicates."""
    result = GroupCleanupResult(group_id=group.group_id)

    for i, fi in enumerate(group.files):
        if i == keep_idx:
            continue
        if dry_run:
            result.files_removed += 1
            result.space_freed += fi.size
        else:
            success, error = safe_remove(fi.path)
            if success:
                result.files_removed += 1
                result.space_freed += fi.size
            elif error:
                result.errors.append(error)

    return result


def cleanup_group_hardlink(
    group: DuplicateGroup,
    keep_idx: int = 0,
    dry_run: bool = True,
) -> GroupCleanupResult:
    """Clean up a group by replacing with hardlinks."""
    result = GroupCleanupResult(group_id=group.group_id)
    keeper = group.files[keep_idx]

    for i, fi in enumerate(group.files):
        if i == keep_idx:
            continue
        if dry_run:
            result.hardlinks_created += 1
            result.space_freed += fi.size
        else:
            success, error = create_hardlink(keeper.path, fi.path)
            if success:
                result.hardlinks_created += 1
                result.space_freed += fi.size
            elif error:
                result.errors.append(error)

    return result


def batch_cleanup(
    groups: list[DuplicateGroup],
    action: str = "hardlink",
    dry_run: bool = True,
) -> BatchCleanupResult:
    """Clean up multiple groups."""
    batch = BatchCleanupResult()

    for group in groups:
        if len(group.files) < 2:
            continue
        if action == "delete":
            result = cleanup_group_delete(group, dry_run=dry_run)
        else:
            result = cleanup_group_hardlink(group, dry_run=dry_run)
        batch.results.append(result)

    return batch


def format_batch_cleanup(batch: BatchCleanupResult) -> str:
    """Format batch cleanup result as text."""
    return (
        f"Cleanup: {batch.total_groups} groups, "
        f"{batch.total_removed} removed, "
        f"{batch.total_freed:,} bytes freed, "
        f"{batch.total_errors} errors"
    )
