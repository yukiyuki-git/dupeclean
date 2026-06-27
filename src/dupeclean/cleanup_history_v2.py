"""File deduplication cleanup history for DupeClean.

Track history of all cleanup operations.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size


@dataclass
class CleanupRecord:
    """A record of a cleanup operation."""

    timestamp: float
    operation: str
    files_affected: int = 0
    space_freed: int = 0
    success: bool = True
    details: dict = field(default_factory=dict)

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)


@dataclass
class CleanupHistoryV2:
    """Complete cleanup history."""

    records: list[CleanupRecord] = field(default_factory=list)

    def add(self, record: CleanupRecord) -> None:
        self.records.append(record)

    def add_cleanup(
        self,
        operation: str,
        files: int,
        freed: int,
        success: bool = True,
    ) -> None:
        self.add(
            CleanupRecord(
                timestamp=time.time(),
                operation=operation,
                files_affected=files,
                space_freed=freed,
                success=success,
            )
        )

    @property
    def total_freed(self) -> int:
        return sum(r.space_freed for r in self.records)

    @property
    def total_operations(self) -> int:
        return len(self.records)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.records if r.success)

    def save(self, path: Path) -> None:
        data = [
            {
                "timestamp": r.timestamp,
                "operation": r.operation,
                "files_affected": r.files_affected,
                "space_freed": r.space_freed,
                "success": r.success,
                "details": r.details,
            }
            for r in self.records
        ]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> CleanupHistoryV2:
        history = cls()
        if not path.exists():
            return history
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                history.records.append(
                    CleanupRecord(
                        timestamp=entry["timestamp"],
                        operation=entry["operation"],
                        files_affected=entry.get("files_affected", 0),
                        space_freed=entry.get("space_freed", 0),
                        success=entry.get("success", True),
                        details=entry.get("details", {}),
                    )
                )
        except (json.JSONDecodeError, OSError):
            pass
        return history


def format_cleanup_history_v2(history: CleanupHistoryV2) -> str:
    """Format cleanup history as text."""
    if not history.records:
        return "No cleanup history."

    lines = [
        f"Cleanup History: {history.total_operations} operations",
        f"Total freed: {format_size(history.total_freed)}",
        f"Success rate: {history.success_count}/{history.total_operations}",
        "",
    ]

    for record in history.records[-10:]:
        import datetime

        dt = datetime.datetime.fromtimestamp(record.timestamp)
        status = "[+]" if record.success else "[X]"
        lines.append(
            f"  {status} [{dt.strftime('%Y-%m-%d %H:%M')}] "
            f"{record.operation}: "
            f"{record.files_affected} files, "
            f"{record.freed_display} freed"
        )

    return "\n".join(lines)
