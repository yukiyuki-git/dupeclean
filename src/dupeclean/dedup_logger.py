"""File deduplication logging module for DupeClean.

Structured logging for dedup operations.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LogEntry:
    """A structured log entry."""

    timestamp: float
    level: str  # "debug", "info", "warning", "error"
    message: str
    module: str = ""
    context: dict = field(default_factory=dict)


@dataclass
class DedupLogger:
    """Structured logger for dedup operations."""

    entries: list[LogEntry] = field(default_factory=list)
    min_level: str = "info"
    max_entries: int = 10000

    _level_priority = {"debug": 0, "info": 1, "warning": 2, "error": 3}

    def _should_log(self, level: str) -> bool:
        return self._level_priority.get(level, 0) >= self._level_priority.get(self.min_level, 1)

    def _add(self, level: str, message: str, module: str = "", **context) -> None:
        if not self._should_log(level):
            return
        if len(self.entries) >= self.max_entries:
            self.entries = self.entries[-self.max_entries // 2 :]
        self.entries.append(
            LogEntry(
                timestamp=time.time(),
                level=level,
                message=message,
                module=module,
                context=context,
            )
        )

    def debug(self, message: str, module: str = "", **context) -> None:
        self._add("debug", message, module, **context)

    def info(self, message: str, module: str = "", **context) -> None:
        self._add("info", message, module, **context)

    def warning(self, message: str, module: str = "", **context) -> None:
        self._add("warning", message, module, **context)

    def error(self, message: str, module: str = "", **context) -> None:
        self._add("error", message, module, **context)

    def get_by_level(self, level: str) -> list[LogEntry]:
        return [e for e in self.entries if e.level == level]

    def get_recent(self, count: int = 50) -> list[LogEntry]:
        return self.entries[-count:]

    def save(self, path: Path) -> None:
        """Save log to JSON file."""
        data = [
            {
                "timestamp": e.timestamp,
                "level": e.level,
                "message": e.message,
                "module": e.module,
                "context": e.context,
            }
            for e in self.entries
        ]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> DedupLogger:
        """Load log from JSON file."""
        logger = cls()
        if not path.exists():
            return logger
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                logger.entries.append(
                    LogEntry(
                        timestamp=entry["timestamp"],
                        level=entry["level"],
                        message=entry["message"],
                        module=entry.get("module", ""),
                        context=entry.get("context", {}),
                    )
                )
        except (json.JSONDecodeError, OSError):
            pass
        return logger


def format_log_entries(entries: list[LogEntry]) -> str:
    """Format log entries as text."""
    if not entries:
        return "No log entries."

    lines = []
    for entry in entries:
        import datetime

        dt = datetime.datetime.fromtimestamp(entry.timestamp)
        level_icons = {"debug": "[D]", "info": "[I]", "warning": "[W]", "error": "[E]"}
        icon = level_icons.get(entry.level, "[?]")
        module = f" ({entry.module})" if entry.module else ""
        lines.append(f"{icon} [{dt.strftime('%H:%M:%S')}] {entry.message}{module}")

    return "\n".join(lines)
