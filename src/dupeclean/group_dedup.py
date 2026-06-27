"""File deduplication group dedup module for DupeClean.

Deduplicate files within groups using hardlinks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size
from .utils import create_hardlink


@dataclass
class DedupAction:
    """A dedup action within a group."""

    source: Path
    target: Path
    size: int = 0
    success: bool = False
    error: str = ""


@dataclass
class GroupDedupResult:
    """Result of deduplication within groups."""

    groups_processed: int = 0
    files_deduped: int = 0
    space_saved: int = 0
    errors: list[str] = field(default_factory=list)
    actions: list[DedupAction] = field(default_factory=list)

    @property
    def saved_display(self) -> str:
        return format_size(self.space_saved)


def dedup_group_hardlink(
    group: DuplicateGroup,
    dry_run: bool = True,
) -> GroupDedupResult:
    """Deduplicate a group using hardlinks."""
    result = GroupDedupResult(groups_processed=1)
    keeper = group.files[0]

    for dupe in group.files[1:]:
        action = DedupAction(
            source=keeper.path,
            target=dupe.path,
            size=group.file_size,
        )

        if dry_run:
            action.success = True
            result.files_deduped += 1
            result.space_saved += dupe.size
        else:
            success, error = create_hardlink(keeper.path, dupe.path)
            action.success = success
            action.error = error
            if success:
                result.files_deduped += 1
                result.space_saved += dupe.size
            elif error:
                result.errors.append(error)

        result.actions.append(action)

    return result


def dedup_groups_hardlink(
    groups: list[DuplicateGroup],
    dry_run: bool = True,
) -> GroupDedupResult:
    """Deduplicate multiple groups using hardlinks."""
    combined = GroupDedupResult()

    for group in groups:
        if len(group.files) < 2:
            continue
        result = dedup_group_hardlink(group, dry_run)
        combined.groups_processed += result.groups_processed
        combined.files_deduped += result.files_deduped
        combined.space_saved += result.space_saved
        combined.errors.extend(result.errors)
        combined.actions.extend(result.actions)

    return combined


def format_dedup_result(result: GroupDedupResult) -> str:
    """Format dedup result as text."""
    return (
        f"Dedup: {result.groups_processed} groups, "
        f"{result.files_deduped} files deduped, "
        f"{result.saved_display} saved"
    )
