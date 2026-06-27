"""File deduplication cleanup history tracker for DupeClean.

Track and query cleanup history across operations.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size


@dataclass
class HistoryRecord:
    """A single history record."""

    timestamp: float
    operation: str
    path: str
    action: str
    size: int = 0
    success: bool = True
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class HistoryTracker:
    """Track cleanup history across operations."""

    records: list[HistoryRecord] = field(default_factory=list)
    max_records: int = 10000

    def add(self, record: HistoryRecord) -> None:
        if len(self.records) >= self.max_records:
            self.records = self.records[-self.max_records // 2 :]
        self.records.append(record)

    def add_cleanup(
        self,
        operation: str,
        path: str,
        action: str,
        size: int = 0,
        success: bool = True,
        error: str = "",
    ) -> None:
        self.add(
            HistoryRecord(
                timestamp=time.time(),
                operation=operation,
                path=path,
                action=action,
                size=size,
                success=success,
                error=error,
            )
        )

    @property
    def total_records(self) -> int:
        return len(self.records)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.records if r.success)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.records if not r.success)

    @property
    def total_size(self) -> int:
        return sum(r.size for r in self.records if r.success)

    def get_by_operation(self, operation: str) -> list[HistoryRecord]:
        return [r for r in self.records if r.operation == operation]

    def get_recent(self, count: int = 50) -> list[HistoryRecord]:
        return self.records[-count:]

    def save(self, path: Path) -> None:
        data = [
            {
                "timestamp": r.timestamp,
                "operation": r.operation,
                "path": r.path,
                "action": r.action,
                "size": r.size,
                "success": r.success,
                "error": r.error,
            }
            for r in self.records
        ]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> HistoryTracker:
        tracker = cls()
        if not path.exists():
            return tracker
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                tracker.records.append(
                    HistoryRecord(
                        timestamp=entry["timestamp"],
                        operation=entry["operation"],
                        path=entry["path"],
                        action=entry["action"],
                        size=entry.get("size", 0),
                        success=entry.get("success", True),
                        error=entry.get("error", ""),
                    )
                )
        except (json.JSONDecodeError, OSError):
            pass
        return tracker


def format_history(tracker: HistoryTracker) -> str:
    """Format history as text."""
    if not tracker.total_records:
        return "No history."

    recent = tracker.get_recent(10)
    lines = [
        f"History: {tracker.total_records:,} records",
        f"  Success: {tracker.success_count:,}",
        f"  Errors: {tracker.error_count:,}",
        f"  Total size: {format_size(tracker.total_size)}",
        "",
    ]

    for record in reversed(recent):
        import datetime

        dt = datetime.datetime.fromtimestamp(record.timestamp)
        status = "[+]" if record.success else "[X]"
        lines.append(
            f"  {status} [{dt.strftime('%H:%M:%S')}] "
            f"{record.action}: {record.path} ({record.size_display})"
        )

    return "\n".join(lines)
