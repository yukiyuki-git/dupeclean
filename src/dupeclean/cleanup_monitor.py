"""File deduplication cleanup monitor for DupeClean.

Monitor cleanup operations in real-time.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class MonitorUpdate:
    """A monitor update."""

    timestamp: float
    event: str
    message: str
    data: dict = field(default_factory=dict)


@dataclass
class CleanupMonitorV2:
    """Enhanced cleanup monitor."""

    updates: list[MonitorUpdate] = field(default_factory=list)
    start_time: float = 0.0
    is_running: bool = False

    def start(self) -> None:
        self.is_running = True
        self.start_time = time.time()
        self._emit("start", "Cleanup started")

    def update(self, event: str, message: str, **data) -> None:
        if self.is_running:
            self._emit(event, message, **data)

    def complete(self, message: str, **data) -> None:
        self.is_running = False
        self._emit("complete", message, **data)

    def error(self, message: str, **data) -> None:
        self._emit("error", message, **data)

    def stop(self) -> None:
        self.is_running = False

    def _emit(self, event: str, message: str, **data) -> None:
        self.updates.append(
            MonitorUpdate(
                timestamp=time.time(),
                event=event,
                message=message,
                data=data,
            )
        )

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        return time.time() - self.start_time

    @property
    def update_count(self) -> int:
        return len(self.updates)

    def get_recent(self, count: int = 10) -> list[MonitorUpdate]:
        return self.updates[-count:]


def format_monitor_v2(monitor: CleanupMonitorV2) -> str:
    """Format monitor status as text."""
    status = "RUNNING" if monitor.is_running else "IDLE"
    lines = [
        f"Monitor: {status} ({monitor.update_count} updates)",
        f"  Elapsed: {monitor.elapsed:.1f}s",
    ]

    recent = monitor.get_recent(5)
    if recent:
        lines.append("\n  Recent:")
        for u in reversed(recent):
            import datetime

            dt = datetime.datetime.fromtimestamp(u.timestamp)
            lines.append(f"    [{dt.strftime('%H:%M:%S')}] {u.event}: {u.message}")

    return "\n".join(lines)
