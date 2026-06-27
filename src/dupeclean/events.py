"""File deduplication cleanup event module for DupeClean.

Define and manage cleanup events.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class CleanupEvent:
    """A cleanup event."""

    event_type: str
    timestamp: float
    data: dict = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        return self.event_type == "error"

    @property
    def is_success(self) -> bool:
        return self.event_type == "success"


@dataclass
class EventManager:
    """Manage cleanup events."""

    events: list[CleanupEvent] = field(default_factory=list)
    max_events: int = 1000

    def emit(self, event_type: str, **data) -> None:
        """Emit an event."""
        if len(self.events) >= self.max_events:
            self.events = self.events[-self.max_events // 2 :]
        self.events.append(
            CleanupEvent(
                event_type=event_type,
                timestamp=time.time(),
                data=data,
            )
        )

    def success(self, message: str, **data) -> None:
        self.emit("success", message=message, **data)

    def error(self, message: str, **data) -> None:
        self.emit("error", message=message, **data)

    def info(self, message: str, **data) -> None:
        self.emit("info", message=message, **data)

    @property
    def count(self) -> int:
        return len(self.events)

    def get_recent(self, count: int = 10) -> list[CleanupEvent]:
        return self.events[-count:]

    def get_by_type(self, event_type: str) -> list[CleanupEvent]:
        return [e for e in self.events if e.event_type == event_type]


def format_events(manager: EventManager) -> str:
    """Format events as text."""
    if not manager.count:
        return "No events."

    recent = manager.get_recent(5)
    lines = [f"Events ({manager.count} total):", ""]
    for event in reversed(recent):
        import datetime

        dt = datetime.datetime.fromtimestamp(event.timestamp)
        msg = event.data.get("message", event.event_type)
        lines.append(f"  [{dt.strftime('%H:%M:%S')}] {event.event_type}: {msg}")
    return "\n".join(lines)
