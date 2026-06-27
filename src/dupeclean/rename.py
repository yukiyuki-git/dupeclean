"""File rename module for DupeClean.

Batch rename files with patterns, sequences, and metadata.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo


@dataclass
class RenameAction:
    """A single rename action."""

    old_path: Path
    new_path: Path
    reason: str = ""


@dataclass
class RenamePlan:
    """A batch rename plan."""

    actions: list[RenameAction] = field(default_factory=list)
    dry_run: bool = True

    @property
    def count(self) -> int:
        return len(self.actions)


def rename_sequential(
    files: list[FileInfo],
    pattern: str = "{index:04d}_{original}",
    start: int = 1,
) -> RenamePlan:
    """Rename files with sequential numbering.

    Args:
        files: Files to rename.
        pattern: Name pattern with {index}, {original}, {ext}.
        start: Starting index.

    Returns:
        RenamePlan with all actions.
    """
    plan = RenamePlan()

    for i, fi in enumerate(files, start):
        original = fi.path.stem
        ext = fi.path.suffix
        new_name = pattern.format(index=i, original=original, ext=ext)
        if not new_name.endswith(ext):
            new_name += ext

        new_path = fi.path.parent / new_name
        if new_path != fi.path:
            plan.actions.append(
                RenameAction(
                    old_path=fi.path,
                    new_path=new_path,
                    reason=f"sequential #{i}",
                )
            )

    return plan


def rename_replace(
    files: list[FileInfo],
    find: str,
    replace: str,
) -> RenamePlan:
    """Rename files by replacing text in filename."""
    plan = RenamePlan()

    for fi in files:
        new_name = fi.path.name.replace(find, replace)
        if new_name != fi.path.name:
            plan.actions.append(
                RenameAction(
                    old_path=fi.path,
                    new_path=fi.path.parent / new_name,
                    reason=f"replace '{find}' -> '{replace}'",
                )
            )

    return plan


def rename_lowercase(files: list[FileInfo]) -> RenamePlan:
    """Rename files to lowercase."""
    plan = RenamePlan()

    for fi in files:
        new_name = fi.path.name.lower()
        if new_name != fi.path.name:
            plan.actions.append(
                RenameAction(
                    old_path=fi.path,
                    new_path=fi.path.parent / new_name,
                    reason="lowercase",
                )
            )

    return plan


def rename_add_prefix(files: list[FileInfo], prefix: str) -> RenamePlan:
    """Add prefix to filenames."""
    plan = RenamePlan()

    for fi in files:
        new_name = prefix + fi.path.name
        plan.actions.append(
            RenameAction(
                old_path=fi.path,
                new_path=fi.path.parent / new_name,
                reason=f"prefix '{prefix}'",
            )
        )

    return plan


def rename_add_suffix(files: list[FileInfo], suffix: str) -> RenamePlan:
    """Add suffix to filenames (before extension)."""
    plan = RenamePlan()

    for fi in files:
        new_name = fi.path.stem + suffix + fi.path.suffix
        plan.actions.append(
            RenameAction(
                old_path=fi.path,
                new_path=fi.path.parent / new_name,
                reason=f"suffix '{suffix}'",
            )
        )

    return plan


def rename_by_date(
    files: list[FileInfo],
    pattern: str = "{date}_{original}{ext}",
) -> RenamePlan:
    """Rename files using their modification date."""
    plan = RenamePlan()

    for fi in files:
        date_str = time.strftime("%Y%m%d", time.localtime(fi.mtime))
        original = fi.path.stem
        ext = fi.path.suffix
        new_name = pattern.format(date=date_str, original=original, ext=ext)
        if not new_name.endswith(ext):
            new_name += ext

        new_path = fi.path.parent / new_name
        if new_path != fi.path:
            plan.actions.append(
                RenameAction(
                    old_path=fi.path,
                    new_path=new_path,
                    reason=f"date {date_str}",
                )
            )

    return plan


def execute_rename(plan: RenamePlan, dry_run: bool = True) -> dict:
    """Execute a rename plan.

    Returns:
        Dict with succeeded, failed, errors.
    """
    succeeded = 0
    failed = 0
    errors: list[str] = []

    for action in plan.actions:
        if dry_run:
            succeeded += 1
            continue

        try:
            if action.new_path.exists():
                # Handle conflict
                counter = 1
                stem = action.new_path.stem
                suffix = action.new_path.suffix
                while action.new_path.exists():
                    action.new_path = action.new_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

            action.old_path.rename(action.new_path)
            succeeded += 1
        except OSError as e:
            failed += 1
            errors.append(f"{action.old_path}: {e}")

    return {
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors,
    }


def format_rename_plan(plan: RenamePlan) -> str:
    """Format a rename plan as text."""
    if not plan.actions:
        return "No renames needed."

    lines = [f"Rename plan: {plan.count} files", ""]
    for action in plan.actions[:20]:
        lines.append(f"  {action.old_path.name} -> {action.new_path.name}  [{action.reason}]")

    if plan.count > 20:
        lines.append(f"\n  ... and {plan.count - 20} more")

    return "\n".join(lines)
