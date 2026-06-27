"""File deduplication cleanup session module for DupeClean.

Manage cleanup sessions with state tracking.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .models import format_size


@dataclass
class SessionState:
    """State of a cleanup session."""

    session_id: str
    status: str = "idle"  # idle, scanning, analyzing, cleaning, done
    start_time: float = 0.0
    end_time: float = 0.0
    files_scanned: int = 0
    groups_found: int = 0
    files_cleaned: int = 0
    space_freed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        end = self.end_time if self.end_time > 0 else time.time()
        return end - self.start_time

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)

    def start(self) -> None:
        self.status = "scanning"
        self.start_time = time.time()

    def complete(self) -> None:
        self.status = "done"
        self.end_time = time.time()


class CleanupSession:
    """Manage a cleanup session."""

    def __init__(self, session_id: str) -> None:
        self.state = SessionState(session_id=session_id)
        self._events: list[tuple[float, str]] = []

    def start(self) -> None:
        self.state.start()
        self._log("Session started")

    def set_status(self, status: str) -> None:
        self.state.status = status
        self._log(f"Status: {status}")

    def record_scan(self, file_count: int) -> None:
        self.state.files_scanned = file_count
        self._log(f"Scanned {file_count} files")

    def record_groups(self, group_count: int) -> None:
        self.state.groups_found = group_count
        self._log(f"Found {group_count} groups")

    def record_cleanup(self, files_cleaned: int, space_freed: int) -> None:
        self.state.files_cleaned += files_cleaned
        self.state.space_freed += space_freed
        self._log(f"Cleaned {files_cleaned} files, freed {format_size(space_freed)}")

    def record_error(self, error: str) -> None:
        self.state.errors.append(error)
        self._log(f"Error: {error}")

    def complete(self) -> None:
        self.state.complete()
        self._log("Session completed")

    def _log(self, message: str) -> None:
        self._events.append((time.time(), message))

    @property
    def events(self) -> list[tuple[float, str]]:
        return list(self._events)


def format_session(session: CleanupSession) -> str:
    """Format session as text."""
    s = session.state
    return (
        f"Session: {s.session_id}\n"
        f"  Status: {s.status}\n"
        f"  Files scanned: {s.files_scanned:,}\n"
        f"  Groups found: {s.groups_found:,}\n"
        f"  Files cleaned: {s.files_cleaned:,}\n"
        f"  Space freed: {s.freed_display}\n"
        f"  Errors: {len(s.errors)}\n"
        f"  Elapsed: {s.elapsed:.1f}s"
    )
