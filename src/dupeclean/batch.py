"""Batch file operations module for DupeClean.

Perform bulk operations on files matching criteria:
- Batch rename with patterns
- Batch move to directory
- Batch delete with confirmation
- Batch compress
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size
from .utils import safe_remove


@dataclass
class BatchAction:
    """A single batch action."""

    source: Path
    destination: Path | None = None
    action: str = "move"  # move, copy, delete, rename
    new_name: str | None = None


@dataclass
class BatchResult:
    """Result of a batch operation."""

    action_type: str
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    bytes_processed: int = 0

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.succeeded / self.total) * 100

    @property
    def bytes_display(self) -> str:
        return format_size(self.bytes_processed)


def batch_move(
    files: list[FileInfo],
    dest_dir: Path,
    dry_run: bool = True,
) -> BatchResult:
    """Move files to a destination directory.

    Args:
        files: Files to move.
        dest_dir: Destination directory.
        dry_run: If True, don't actually move.

    Returns:
        BatchResult with operation details.
    """
    result = BatchResult(action_type="move", total=len(files))

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    for fi in files:
        target = dest_dir / fi.path.name
        # Handle name conflicts
        counter = 1
        while target.exists():
            target = dest_dir / f"{fi.path.stem}_{counter}{fi.path.suffix}"
            counter += 1

        if dry_run:
            result.succeeded += 1
            result.bytes_processed += fi.size
            continue

        try:
            shutil.move(str(fi.path), str(target))
            result.succeeded += 1
            result.bytes_processed += fi.size
        except OSError as e:
            result.failed += 1
            result.errors.append(f"{fi.path}: {e}")

    return result


def batch_copy(
    files: list[FileInfo],
    dest_dir: Path,
    dry_run: bool = True,
) -> BatchResult:
    """Copy files to a destination directory."""
    result = BatchResult(action_type="copy", total=len(files))

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    for fi in files:
        target = dest_dir / fi.path.name
        counter = 1
        while target.exists():
            target = dest_dir / f"{fi.path.stem}_{counter}{fi.path.suffix}"
            counter += 1

        if dry_run:
            result.succeeded += 1
            result.bytes_processed += fi.size
            continue

        try:
            shutil.copy2(str(fi.path), str(target))
            result.succeeded += 1
            result.bytes_processed += fi.size
        except OSError as e:
            result.failed += 1
            result.errors.append(f"{fi.path}: {e}")

    return result


def batch_delete(
    files: list[FileInfo],
    dry_run: bool = True,
) -> BatchResult:
    """Delete files."""
    result = BatchResult(action_type="delete", total=len(files))

    for fi in files:
        if dry_run:
            result.succeeded += 1
            result.bytes_processed += fi.size
            continue

        success, error = safe_remove(fi.path)
        if success:
            result.succeeded += 1
            result.bytes_processed += fi.size
        else:
            result.failed += 1
            if error:
                result.errors.append(error)

    return result


def batch_rename(
    files: list[FileInfo],
    pattern: str,
    replacement: str,
    dry_run: bool = True,
) -> BatchResult:
    """Rename files using pattern substitution.

    Args:
        files: Files to rename.
        pattern: String to find in filename.
        replacement: String to replace with.

    Returns:
        BatchResult with operation details.
    """
    result = BatchResult(action_type="rename", total=len(files))

    for fi in files:
        old_name = fi.path.name
        new_name = old_name.replace(pattern, replacement)

        if old_name == new_name:
            result.skipped += 1
            continue

        new_path = fi.path.parent / new_name

        if dry_run:
            result.succeeded += 1
            continue

        try:
            fi.path.rename(new_path)
            result.succeeded += 1
        except OSError as e:
            result.failed += 1
            result.errors.append(f"{fi.path}: {e}")

    return result


def format_batch_result(result: BatchResult) -> str:
    """Format batch result as text."""
    lines = [
        f"Batch {result.action_type}:",
        f"  Total: {result.total}",
        f"  Succeeded: {result.succeeded}",
        f"  Failed: {result.failed}",
        f"  Skipped: {result.skipped}",
    ]
    if result.bytes_processed > 0:
        lines.append(f"  Data: {result.bytes_display}")
    if result.errors:
        lines.append("\n  Errors:")
        for err in result.errors[:10]:
            lines.append(f"    {err}")
    return "\n".join(lines)
