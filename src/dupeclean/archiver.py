"""File deduplication file archiver module for DupeClean.

Archive old files to compressed storage.
"""

from __future__ import annotations

import tarfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class ArchiveAction:
    """An archive action."""

    source: Path
    archive: Path
    size: int = 0
    success: bool = False
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class ArchiveResult:
    """Result of archive operation."""

    actions: list[ArchiveAction] = field(default_factory=list)
    archive_path: Path | None = None
    original_size: int = 0
    archive_size: int = 0
    duration: float = 0.0

    @property
    def total(self) -> int:
        return len(self.actions)

    @property
    def succeeded(self) -> int:
        return sum(1 for a in self.actions if a.success)

    @property
    def compression_ratio(self) -> float:
        if self.original_size == 0:
            return 0.0
        return self.archive_size / self.original_size


def archive_files(
    files: list[FileInfo],
    archive_path: Path,
    dry_run: bool = True,
) -> ArchiveResult:
    """Archive files to a tar.gz archive."""
    result = ArchiveResult(archive_path=archive_path)
    start = time.monotonic()

    if dry_run:
        for fi in files:
            result.actions.append(
                ArchiveAction(
                    source=fi.path,
                    archive=archive_path,
                    size=fi.size,
                    success=True,
                )
            )
            result.original_size += fi.size
        result.duration = time.monotonic() - start
        return result

    try:
        with tarfile.open(str(archive_path), "w:gz") as tar:
            for fi in files:
                try:
                    tar.add(str(fi.path), arcname=fi.path.name)
                    result.actions.append(
                        ArchiveAction(
                            source=fi.path,
                            archive=archive_path,
                            size=fi.size,
                            success=True,
                        )
                    )
                    result.original_size += fi.size
                except OSError as e:
                    result.actions.append(
                        ArchiveAction(
                            source=fi.path,
                            archive=archive_path,
                            size=fi.size,
                            error=str(e),
                        )
                    )

        result.archive_size = archive_path.stat().st_size
    except OSError as e:
        result.actions.append(
            ArchiveAction(
                source=Path(""),
                archive=archive_path,
                error=str(e),
            )
        )

    result.duration = time.monotonic() - start
    return result


def format_archive_result(result: ArchiveResult) -> str:
    """Format archive result as text."""
    lines = [
        f"Archive: {result.succeeded}/{result.total} files",
        f"  Original: {format_size(result.original_size)}",
        f"  Archive: {format_size(result.archive_size)}",
        f"  Ratio: {result.compression_ratio:.1%}",
        f"  Duration: {result.duration:.1f}s",
    ]
    return "\n".join(lines)
