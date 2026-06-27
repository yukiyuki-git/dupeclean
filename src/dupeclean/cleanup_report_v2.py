"""File deduplication cleanup reporter for DupeClean.

Generate detailed cleanup reports after operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class CleanupStats:
    """Statistics from a cleanup operation."""

    files_before: int = 0
    files_after: int = 0
    size_before: int = 0
    size_after: int = 0
    files_deleted: int = 0
    files_hardlinked: int = 0
    files_skipped: int = 0
    errors: int = 0
    duration: float = 0.0

    @property
    def space_freed(self) -> int:
        return self.size_before - self.size_after

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)

    @property
    def reduction_pct(self) -> float:
        if self.size_before == 0:
            return 0.0
        return (self.space_freed / self.size_before) * 100


@dataclass
class CleanupReportV2:
    """Detailed cleanup report."""

    stats: CleanupStats
    operation_id: str
    timestamp: float
    strategy: str
    details: list[str] = field(default_factory=list)

    def render(self) -> str:
        """Render report as text."""
        import datetime

        dt = datetime.datetime.fromtimestamp(self.timestamp)
        lines = [
            f"Cleanup Report: {self.operation_id}",
            "=" * 40,
            f"  Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Strategy: {self.strategy}",
            f"  Duration: {self.stats.duration:.1f}s",
            "",
            f"  Files before: {self.stats.files_before:,}",
            f"  Files after:  {self.stats.files_after:,}",
            f"  Deleted: {self.stats.files_deleted:,}",
            f"  Hardlinked: {self.stats.files_hardlinked:,}",
            f"  Skipped: {self.stats.files_skipped:,}",
            f"  Errors: {self.stats.errors}",
            "",
            f"  Size before: {format_size(self.stats.size_before)}",
            f"  Size after:  {format_size(self.stats.size_after)}",
            f"  Freed:       {self.stats.freed_display} ({self.stats.reduction_pct:.1f}%)",
        ]

        if self.details:
            lines.append("\n  Details:")
            for detail in self.details[:20]:
                lines.append(f"    {detail}")

        return "\n".join(lines)


def create_report(
    stats: CleanupStats,
    strategy: str = "shortest",
    details: list[str] | None = None,
) -> CleanupReportV2:
    """Create a cleanup report."""
    import time as t

    return CleanupReportV2(
        stats=stats,
        operation_id=f"cleanup_{int(t.time())}",
        timestamp=t.time(),
        strategy=strategy,
        details=details or [],
    )


def format_cleanup_report_v2(report: CleanupReportV2) -> str:
    """Format report as text."""
    return report.render()
