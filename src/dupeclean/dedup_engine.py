"""File deduplication engine for DupeClean.

Performs actual deduplication by replacing duplicates with
hard links to a single canonical copy. Supports:
- Content-addressable dedup (same content -> same inode)
- Safe dedup with verification
- Rollback support
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size
from .utils import create_hardlink, is_same_file


@dataclass
class DedupAction:
    """A single dedup action."""
    source: Path  # The canonical file to keep
    target: Path  # The duplicate to replace
    method: str  # "hardlink" or "symlink"
    size: int


@dataclass
class DedupPlan:
    """A complete deduplication plan."""
    actions: list[DedupAction] = field(default_factory=list)
    total_space_saved: int = 0

    @property
    def count(self) -> int:
        return len(self.actions)

    @property
    def savings_display(self) -> str:
        return format_size(self.total_space_saved)


@dataclass
class DedupResult:
    """Result of executing a dedup plan."""
    actions_completed: int = 0
    actions_failed: int = 0
    space_saved: int = 0
    errors: list[str] = field(default_factory=list)


def create_dedup_plan(
    groups: list[DuplicateGroup],
    method: str = "hardlink",
) -> DedupPlan:
    """Create a deduplication plan.

    Args:
        groups: Duplicate groups from analysis.
        method: "hardlink" or "symlink".

    Returns:
        DedupPlan with all actions to perform.
    """
    plan = DedupPlan()

    for group in groups:
        if len(group.files) < 2:
            continue

        # Keep the first file as canonical
        canonical = group.files[0]
        for dupe in group.files[1:]:
            plan.actions.append(
                DedupAction(
                    source=canonical.path,
                    target=dupe.path,
                    method=method,
                    size=group.file_size,
                )
            )
            plan.total_space_saved += group.file_size

    return plan


def execute_dedup(
    plan: DedupPlan,
    dry_run: bool = True,
    verify: bool = True,
) -> DedupResult:
    """Execute a deduplication plan.

    Args:
        plan: The dedup plan.
        dry_run: If True, don't actually modify files.
        verify: If True, verify hardlink after creation.

    Returns:
        DedupResult with execution details.
    """
    result = DedupResult()

    for action in plan.actions:
        if dry_run:
            result.actions_completed += 1
            result.space_saved += action.size
            continue

        try:
            if action.method == "hardlink":
                success, error = _do_hardlink(
                    action.source, action.target, verify
                )
            else:
                success, error = _do_symlink(
                    action.source, action.target
                )

            if success:
                result.actions_completed += 1
                result.space_saved += action.size
            else:
                result.actions_failed += 1
                if error:
                    result.errors.append(error)
        except Exception as e:
            result.actions_failed += 1
            result.errors.append(f"{action.target}: {e}")

    return result


def _do_hardlink(
    source: Path, target: Path, verify: bool
) -> tuple[bool, str]:
    """Create a hardlink from target to source."""
    # Backup target first
    backup = target.with_suffix(target.suffix + ".dedup_backup")
    try:
        shutil.copy2(str(target), str(backup))
    except OSError as e:
        return False, f"Backup failed: {e}"

    success, error = create_hardlink(source, target)

    if success and verify and not is_same_file(source, target):
        # Rollback
        shutil.move(str(backup), str(target))
        return False, "Verification failed, rolled back"

    # Clean up backup
    if success:
        import contextlib

        with contextlib.suppress(OSError):
            backup.unlink()

    return success, error


def _do_symlink(
    source: Path, target: Path
) -> tuple[bool, str]:
    """Create a symlink from target to source."""
    try:
        target.unlink()
        target.symlink_to(source)
        return True, ""
    except OSError as e:
        return False, f"Symlink failed: {e}"


def format_dedup_plan(plan: DedupPlan) -> str:
    """Format a dedup plan as text."""
    lines = [
        f"Dedup Plan: {plan.count} actions, "
        f"{plan.savings_display} savings",
        "",
    ]

    for action in plan.actions[:20]:
        lines.append(
            f"  {action.method}: {action.target.name} -> "
            f"{action.source.name}"
        )

    if plan.count > 20:
        lines.append(
            f"\n  ... and {plan.count - 20} more actions"
        )

    return "\n".join(lines)
