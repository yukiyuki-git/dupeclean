"""File deduplication file merger module for DupeClean.

Merge duplicate files by keeping the best version.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class MergeAction:
    """A merge action."""

    group_id: int
    keeper: FileInfo
    removed: list[FileInfo] = field(default_factory=list)
    space_saved: int = 0

    @property
    def saved_display(self) -> str:
        return format_size(self.space_saved)


@dataclass
class MergeResult:
    """Result of merge operations."""

    actions: list[MergeAction] = field(default_factory=list)

    @property
    def total_groups(self) -> int:
        return len(self.actions)

    @property
    def total_saved(self) -> int:
        return sum(a.space_saved for a in self.actions)

    @property
    def total_files_removed(self) -> int:
        return sum(len(a.removed) for a in self.actions)


def select_best_file(files: list[FileInfo]) -> int:
    """Select the best file to keep from a group.

    Strategy: Keep file with shortest path (most likely original).
    """
    return min(range(len(files)), key=lambda i: len(str(files[i].path)))


def merge_group(group: DuplicateGroup) -> MergeAction:
    """Merge a duplicate group by keeping the best file."""
    keep_idx = select_best_file(group.files)
    keeper = group.files[keep_idx]
    removed = [f for i, f in enumerate(group.files) if i != keep_idx]

    return MergeAction(
        group_id=group.group_id,
        keeper=keeper,
        removed=removed,
        space_saved=sum(f.size for f in removed),
    )


def merge_groups(groups: list[DuplicateGroup]) -> MergeResult:
    """Merge multiple duplicate groups."""
    result = MergeResult()
    for group in groups:
        if len(group.files) >= 2:
            result.actions.append(merge_group(group))
    return result


def format_merge_result(result: MergeResult) -> str:
    """Format merge result as text."""
    return (
        f"Merge: {result.total_groups} groups, "
        f"{result.total_files_removed} files removed, "
        f"{format_size(result.total_saved)} saved"
    )
