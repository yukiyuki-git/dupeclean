"""File deduplication cleanup monitor for DupeClean.

Monitor cleanup operations in real-time.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class MonitorEvent:
    """A monitoring event."""

    timestamp: float
    event_type: str  # "start", "progress", "complete", "error"
    message: str
    data: dict = field(default_factory=dict)


@dataclass
class CleanupMonitor:
    """Monitor cleanup operations."""

    events: list[MonitorEvent] = field(default_factory=list)
    start_time: float = 0.0
    _running: bool = False

    def start(self) -> None:
        self._running = True
        self.start_time = time.time()
        self._emit("start", "Cleanup started")

    def progress(self, message: str, **data) -> None:
        if self._running:
            self._emit("progress", message, **data)

    def complete(self, message: str, **data) -> None:
        self._running = False
        self._emit("complete", message, **data)

    def error(self, message: str, **data) -> None:
        self._emit("error", message, **data)

    def stop(self) -> None:
        self._running = False

    def _emit(self, event_type: str, message: str, **data) -> None:
        self.events.append(
            MonitorEvent(
                timestamp=time.time(),
                event_type=event_type,
                message=message,
                data=data,
            )
        )

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.time() - self.start_time

    def get_recent(self, count: int = 10) -> list[MonitorEvent]:
        return self.events[-count:]


def format_monitor(monitor: CleanupMonitor) -> str:
    """Format monitor status as text."""
    status = "RUNNING" if monitor.is_running else "IDLE"
    lines = [
        f"Monitor: {status} ({monitor.event_count} events)",
        f"  Elapsed: {monitor.elapsed:.1f}s",
    ]

    recent = monitor.get_recent(5)
    if recent:
        lines.append("\n  Recent events:")
        for event in reversed(recent):
            import datetime

            dt = datetime.datetime.fromtimestamp(event.timestamp)
            lines.append(f"    [{dt.strftime('%H:%M:%S')}] {event.event_type}: {event.message}")

    return "\n".join(lines)
