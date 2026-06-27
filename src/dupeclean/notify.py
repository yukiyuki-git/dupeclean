"""File notification module for DupeClean.

Send notifications about scan results and cleanup actions.
Supports desktop notifications and log file output.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Notification:
    """A notification message."""

    title: str
    message: str
    level: str = "info"  # info, warning, error, success
    timestamp: float = 0.0
    data: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timestamp == 0:
            self.timestamp = time.time()


@dataclass
class NotificationLog:
    """Persistent notification log."""

    path: Path
    notifications: list[Notification] = field(default_factory=list)
    max_entries: int = 1000

    def add(self, notification: Notification) -> None:
        """Add a notification to the log."""
        self.notifications.append(notification)
        if len(self.notifications) > self.max_entries:
            self.notifications = self.notifications[-self.max_entries :]

    def info(self, title: str, message: str, **data) -> None:
        """Add an info notification."""
        self.add(Notification(title=title, message=message, level="info", data=data))

    def warning(self, title: str, message: str, **data) -> None:
        """Add a warning notification."""
        self.add(Notification(title=title, message=message, level="warning", data=data))

    def error(self, title: str, message: str, **data) -> None:
        """Add an error notification."""
        self.add(Notification(title=title, message=message, level="error", data=data))

    def success(self, title: str, message: str, **data) -> None:
        """Add a success notification."""
        self.add(Notification(title=title, message=message, level="success", data=data))

    def save(self) -> None:
        """Save notifications to file."""
        data = [
            {
                "title": n.title,
                "message": n.message,
                "level": n.level,
                "timestamp": n.timestamp,
                "data": n.data,
            }
            for n in self.notifications
        ]
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> NotificationLog:
        """Load notifications from file."""
        log = cls(path=path)
        if not path.exists():
            return log
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                log.notifications.append(
                    Notification(
                        title=entry["title"],
                        message=entry["message"],
                        level=entry.get("level", "info"),
                        timestamp=entry.get("timestamp", 0),
                        data=entry.get("data", {}),
                    )
                )
        except (json.JSONDecodeError, OSError):
            pass
        return log

    def get_recent(self, count: int = 10) -> list[Notification]:
        """Get recent notifications."""
        return self.notifications[-count:]

    def get_by_level(self, level: str) -> list[Notification]:
        """Get notifications by level."""
        return [n for n in self.notifications if n.level == level]


def format_notification(notification: Notification) -> str:
    """Format a notification as text."""
    import datetime

    dt = datetime.datetime.fromtimestamp(notification.timestamp)
    level_icons = {
        "info": "[i]",
        "warning": "[!]",
        "error": "[X]",
        "success": "[+]",
    }
    icon = level_icons.get(notification.level, "[?]")
    return f"{icon} [{dt.strftime('%H:%M:%S')}] {notification.title}: {notification.message}"


def format_notification_log(log: NotificationLog, count: int = 20) -> str:
    """Format notification log as text."""
    recent = log.get_recent(count)
    if not recent:
        return "No notifications."

    lines = [
        f"Notifications ({len(log.notifications)} total, showing last {len(recent)}):",
        "",
    ]

    for n in reversed(recent):
        lines.append(format_notification(n))

    return "\n".join(lines)
