"""File deduplication scan progress for DupeClean.

Track scan progress with detailed metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .models import format_size


@dataclass
class ScanProgress:
    """Scan progress metrics."""

    total_dirs: int = 0
    dirs_scanned: int = 0
    total_files: int = 0
    files_scanned: int = 0
    bytes_scanned: int = 0
    start_time: float = 0.0

    @property
    def dir_percentage(self) -> float:
        if self.total_dirs == 0:
            return 0.0
        return min(100.0, self.dirs_scanned / self.total_dirs * 100)

    @property
    def file_percentage(self) -> float:
        if self.total_files == 0:
            return 0.0
        return min(100.0, self.files_scanned / self.total_files * 100)

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.monotonic() - self.start_time

    @property
    def files_per_second(self) -> float:
        if self.elapsed <= 0:
            return 0.0
        return self.files_scanned / self.elapsed

    @property
    def bytes_per_second(self) -> float:
        if self.elapsed <= 0:
            return 0.0
        return self.bytes_scanned / self.elapsed

    @property
    def eta_seconds(self) -> float | None:
        if self.files_scanned <= 0 or self.files_per_second <= 0:
            return None
        remaining = self.total_files - self.files_scanned
        return remaining / self.files_per_second

    @property
    def mb_scanned(self) -> str:
        return format_size(self.bytes_scanned)

    def update(self, files: int = 0, dirs: int = 0, bytes_count: int = 0) -> None:
        """Update progress."""
        self.files_scanned += files
        self.dirs_scanned += dirs
        self.bytes_scanned += bytes_count

    def render(self) -> str:
        """Render progress as text."""
        bar_width = 30
        filled = min(bar_width, int(self.file_percentage / 100 * bar_width))
        bar = "█" * filled + "░" * (bar_width - filled)

        parts = [
            f"[{bar}] {self.file_percentage:5.1f}%",
            f"({self.files_scanned}/{self.total_files})",
        ]

        if self.eta_seconds is not None:
            eta = self.eta_seconds
            if eta < 60:
                parts.append(f"ETA {eta:.0f}s")
            else:
                parts.append(f"ETA {eta / 60:.1f}m")

        if self.files_per_second > 0:
            parts.append(f"({self.files_per_second:,.0f} files/s)")

        return " ".join(parts)


def create_scan_progress(
    total_files: int,
    total_dirs: int = 0,
) -> ScanProgress:
    """Create scan progress tracker."""
    return ScanProgress(
        total_files=total_files,
        total_dirs=total_dirs,
        start_time=time.monotonic(),
    )
