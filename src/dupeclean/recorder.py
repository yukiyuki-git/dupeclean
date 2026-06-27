"""File deduplication cleanup recorder for DupeClean.

Record cleanup operations for audit and undo support.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size


@dataclass
class RecordedAction:
    """A recorded cleanup action."""

    timestamp: float
    action_type: str
    source_path: str
    target_path: str = ""
    size: int = 0
    success: bool = True
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupRecorder:
    """Record cleanup operations."""

    actions: list[RecordedAction] = field(default_factory=list)

    def record(
        self,
        action_type: str,
        source: str,
        target: str = "",
        size: int = 0,
        success: bool = True,
        error: str = "",
    ) -> None:
        """Record an action."""
        self.actions.append(
            RecordedAction(
                timestamp=time.time(),
                action_type=action_type,
                source_path=source,
                target_path=target,
                size=size,
                success=success,
                error=error,
            )
        )

    @property
    def total_actions(self) -> int:
        return len(self.actions)

    @property
    def success_count(self) -> int:
        return sum(1 for a in self.actions if a.success)

    @property
    def total_size(self) -> int:
        return sum(a.size for a in self.actions if a.success)

    def save(self, path: Path) -> None:
        """Save recording to file."""
        data = [
            {
                "timestamp": a.timestamp,
                "action": a.action_type,
                "source": a.source_path,
                "target": a.target_path,
                "size": a.size,
                "success": a.success,
                "error": a.error,
            }
            for a in self.actions
        ]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> CleanupRecorder:
        """Load recording from file."""
        recorder = cls()
        if not path.exists():
            return recorder
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                recorder.actions.append(
                    RecordedAction(
                        timestamp=entry["timestamp"],
                        action_type=entry["action"],
                        source_path=entry["source"],
                        target_path=entry.get("target", ""),
                        size=entry.get("size", 0),
                        success=entry.get("success", True),
                        error=entry.get("error", ""),
                    )
                )
        except (json.JSONDecodeError, OSError):
            pass
        return recorder


def format_recording(recorder: CleanupRecorder) -> str:
    """Format recording as text."""
    if not recorder.total_actions:
        return "No recorded actions."

    lines = [
        f"Recording: {recorder.total_actions} actions",
        f"  Success: {recorder.success_count}",
        f"  Total size: {format_size(recorder.total_size)}",
    ]
    return "\n".join(lines)
