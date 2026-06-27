"""File deduplication cleanup report for DupeClean.

Generate detailed cleanup reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class CleanupReportEntry:
    """A single entry in the cleanup report."""

    file_path: str
    action: str
    size: int = 0
    success: bool = True
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupReport:
    """Complete cleanup report."""

    operation_id: str
    entries: list[CleanupReportEntry] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    @property
    def success_count(self) -> int:
        return sum(1 for e in self.entries if e.success)

    @property
    def error_count(self) -> int:
        return sum(1 for e in self.entries if not e.success)

    @property
    def total_freed(self) -> int:
        return sum(e.size for e in self.entries if e.success)

    @property
    def freed_display(self) -> str:
        return format_size(self.total_freed)

    def add(self, entry: CleanupReportEntry) -> None:
        self.entries.append(entry)

    def render(self) -> str:
        """Render report as text."""
        lines = [
            f"Cleanup Report: {self.operation_id}",
            "=" * 40,
            f"  Entries: {self.total_entries:,}",
            f"  Success: {self.success_count:,}",
            f"  Errors: {self.error_count:,}",
            f"  Freed: {self.freed_display}",
            "",
        ]

        for entry in self.entries[:20]:
            status = "[+]" if entry.success else "[X]"
            lines.append(f"  {status} {entry.action}: {entry.file_path} ({entry.size_display})")

        if self.total_entries > 20:
            lines.append(f"\n  ... and {self.total_entries - 20} more")

        return "\n".join(lines)


def generate_cleanup_report(
    operation_id: str,
    files: list[tuple[str, str, int, bool, str]],
) -> CleanupReport:
    """Generate a cleanup report from operation data.

    Args:
        operation_id: Unique operation identifier.
        files: List of (path, action, size, success, error).
    """
    report = CleanupReport(operation_id=operation_id)
    for path, action, size, success, error in files:
        report.add(
            CleanupReportEntry(
                file_path=path,
                action=action,
                size=size,
                success=success,
                error=error,
            )
        )
    return report
