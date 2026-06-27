"""File deduplication file deduplicator module for DupeClean.

Deduplicate files by replacing duplicates with hard links.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size
from .utils import create_hardlink


@dataclass
class DedupAction:
    """A dedup action."""

    source: Path
    target: Path
    size: int = 0
    success: bool = False
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class DedupResult:
    """Result of deduplication."""

    actions: list[DedupAction] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.actions)

    @property
    def succeeded(self) -> int:
        return sum(1 for a in self.actions if a.success)

    @property
    def failed(self) -> int:
        return sum(1 for a in self.actions if not a.success)

    @property
    def space_saved(self) -> int:
        return sum(a.size for a in self.actions if a.success)


def deduplicate_group(
    group: DuplicateGroup,
    dry_run: bool = True,
) -> DedupResult:
    """Deduplicate a single group."""
    result = DedupResult()

    if len(group.files) < 2:
        return result

    canonical = group.files[0]
    for dupe in group.files[1:]:
        action = DedupAction(
            source=canonical.path,
            target=dupe.path,
            size=group.file_size,
        )

        if dry_run:
            action.success = True
        else:
            success, error = create_hardlink(canonical.path, dupe.path)
            action.success = success
            action.error = error

        result.actions.append(action)

    return result


def deduplicate_groups(
    groups: list[DuplicateGroup],
    dry_run: bool = True,
) -> DedupResult:
    """Deduplicate multiple groups."""
    combined = DedupResult()

    for group in groups:
        result = deduplicate_group(group, dry_run)
        combined.actions.extend(result.actions)

    return combined


def format_dedup_result(result: DedupResult) -> str:
    """Format dedup result as text."""
    return (
        f"Dedup: {result.succeeded}/{result.total} succeeded, "
        f"{format_size(result.space_saved)} saved"
    )
