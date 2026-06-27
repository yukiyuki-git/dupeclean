"""File deduplication cleanup notification module for DupeClean.

Send notifications about cleanup operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class CleanupNotification:
    """A cleanup notification."""

    timestamp: float
    title: str
    message: str
    level: str = "info"  # info, success, warning, error
    data: dict = field(default_factory=dict)


@dataclass
class NotificationManager:
    """Manage cleanup notifications."""

    notifications: list[CleanupNotification] = field(default_factory=list)
    max_notifications: int = 100

    def notify(
        self,
        title: str,
        message: str,
        level: str = "info",
        **data,
    ) -> None:
        if len(self.notifications) >= self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications // 2 :]
        self.notifications.append(
            CleanupNotification(
                timestamp=time.time(),
                title=title,
                message=message,
                level=level,
                data=data,
            )
        )

    def success(self, title: str, message: str, **data) -> None:
        self.notify(title, message, "success", **data)

    def warning(self, title: str, message: str, **data) -> None:
        self.notify(title, message, "warning", **data)

    def error(self, title: str, message: str, **data) -> None:
        self.notify(title, message, "error", **data)

    @property
    def count(self) -> int:
        return len(self.notifications)

    def get_recent(self, count: int = 10) -> list[CleanupNotification]:
        return self.notifications[-count:]


def format_notifications(manager: NotificationManager) -> str:
    """Format notifications as text."""
    if not manager.count:
        return "No notifications."

    recent = manager.get_recent(5)
    level_icons = {
        "info": "[i]",
        "success": "[+]",
        "warning": "[!]",
        "error": "[X]",
    }
    lines = [f"Notifications ({manager.count} total):", ""]
    for n in reversed(recent):
        import datetime

        dt = datetime.datetime.fromtimestamp(n.timestamp)
        icon = level_icons.get(n.level, "[?]")
        lines.append(f"  {icon} [{dt.strftime('%H:%M')}] {n.title}: {n.message}")
    return "\n".join(lines)
