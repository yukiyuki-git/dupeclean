"""File deduplication file mover module for DupeClean.

Move files between directories with dedup awareness.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class MoveAction:
    """A file move action."""

    source: Path
    destination: Path
    size: int = 0
    success: bool = False
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class MoveResult:
    """Result of a batch move operation."""

    actions: list[MoveAction] = field(default_factory=list)

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


def move_file(source: Path, destination: Path) -> MoveAction:
    """Move a single file."""
    action = MoveAction(
        source=source,
        destination=destination,
        size=source.stat().st_size if source.exists() else 0,
    )

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        action.success = True
    except OSError as e:
        action.error = str(e)

    return action


def move_files(
    files: list[FileInfo],
    destination: Path,
    dry_run: bool = True,
) -> MoveResult:
    """Move multiple files to destination."""
    result = MoveResult()

    for fi in files:
        target = destination / fi.path.name
        action = MoveAction(
            source=fi.path,
            destination=target,
            size=fi.size,
        )

        if dry_run:
            action.success = True
        else:
            try:
                destination.mkdir(parents=True, exist_ok=True)
                shutil.move(str(fi.path), str(target))
                action.success = True
            except OSError as e:
                action.error = str(e)

        result.actions.append(action)

    return result


def format_move_result(result: MoveResult) -> str:
    """Format move result as text."""
    return (
        f"Move: {result.succeeded}/{result.total} succeeded, {format_size(result.total_size)} moved"
    )
