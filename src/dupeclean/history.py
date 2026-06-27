"""Cleanup history module for DupeClean.

Track all cleanup operations with before/after snapshots.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size

HISTORY_FILE = "cleanup_history.json"


@dataclass
class CleanupRecord:
    """A single cleanup operation record."""

    timestamp: float
    action: str  # "delete", "hardlink", "move", "rename"
    path: str
    size_freed: int = 0
    success: bool = True
    error: str = ""
    group_id: int = -1


@dataclass
class CleanupSession:
    """A cleanup session with multiple records."""

    timestamp: float
    target: str
    records: list[CleanupRecord] = field(default_factory=list)

    @property
    def total_freed(self) -> int:
        return sum(r.size_freed for r in self.records)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.records if r.success)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.records if not r.success)


@dataclass
class CleanupHistory:
    """Complete cleanup history."""

    sessions: list[CleanupSession] = field(default_factory=list)

    def add_session(self, session: CleanupSession) -> None:
        """Add a cleanup session to history."""
        self.sessions.append(session)

    def total_freed(self) -> int:
        """Total bytes freed across all sessions."""
        return sum(s.total_freed for s in self.sessions)

    def total_operations(self) -> int:
        """Total cleanup operations."""
        return sum(len(s.records) for s in self.sessions)

    def save(self, path: Path) -> None:
        """Save history to JSON file."""
        data = {
            "version": 1,
            "sessions": [
                {
                    "timestamp": s.timestamp,
                    "target": s.target,
                    "records": [
                        {
                            "timestamp": r.timestamp,
                            "action": r.action,
                            "path": r.path,
                            "size_freed": r.size_freed,
                            "success": r.success,
                            "error": r.error,
                            "group_id": r.group_id,
                        }
                        for r in s.records
                    ],
                }
                for s in self.sessions
            ],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> CleanupHistory:
        """Load history from JSON file."""
        history = cls()
        if not path.exists():
            return history

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return history

        for s in data.get("sessions", []):
            session = CleanupSession(
                timestamp=s["timestamp"],
                target=s["target"],
            )
            for r in s.get("records", []):
                session.records.append(
                    CleanupRecord(
                        timestamp=r["timestamp"],
                        action=r["action"],
                        path=r["path"],
                        size_freed=r.get("size_freed", 0),
                        success=r.get("success", True),
                        error=r.get("error", ""),
                        group_id=r.get("group_id", -1),
                    )
                )
            history.sessions.append(session)

        return history


def format_history(history: CleanupHistory) -> str:
    """Format cleanup history as text."""
    if not history.sessions:
        return "No cleanup history."

    lines = [
        f"Cleanup History: {len(history.sessions)} sessions",
        f"Total freed: {format_size(history.total_freed())}",
        f"Total operations: {history.total_operations():,}",
        "",
    ]

    for session in history.sessions[-10:]:  # Last 10
        import datetime

        dt = datetime.datetime.fromtimestamp(session.timestamp)
        lines.append(f"  [{dt.strftime('%Y-%m-%d %H:%M')}] {session.target}")
        lines.append(
            f"    {session.success_count} succeeded, "
            f"{session.error_count} errors, "
            f"{format_size(session.total_freed)} freed"
        )

    return "\n".join(lines)
