"""File deduplication file copier module for DupeClean.

Copy files with dedup awareness.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class CopyAction:
    """A file copy action."""

    source: Path
    destination: Path
    size: int = 0
    success: bool = False
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CopyResult:
    """Result of a batch copy operation."""

    actions: list[CopyAction] = field(default_factory=list)

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
    def total_size(self) -> int:
        return sum(a.size for a in self.actions if a.success)


def copy_file(source: Path, destination: Path) -> CopyAction:
    """Copy a single file."""
    action = CopyAction(
        source=source,
        destination=destination,
        size=source.stat().st_size if source.exists() else 0,
    )

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(destination))
        action.success = True
    except OSError as e:
        action.error = str(e)

    return action


def copy_files(
    files: list[FileInfo],
    destination: Path,
    dry_run: bool = True,
) -> CopyResult:
    """Copy multiple files to destination."""
    result = CopyResult()

    for fi in files:
        target = destination / fi.path.name
        action = CopyAction(
            source=fi.path,
            destination=target,
            size=fi.size,
        )

        if dry_run:
            action.success = True
        else:
            try:
                destination.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(fi.path), str(target))
                action.success = True
            except OSError as e:
                action.error = str(e)

        result.actions.append(action)

    return result


def format_copy_result(result: CopyResult) -> str:
    """Format copy result as text."""
    return (
        f"Copy: {result.succeeded}/{result.total} succeeded, "
        f"{format_size(result.total_size)} copied"
    )
