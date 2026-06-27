"""Watch mode for DupeClean — monitor directory changes in real-time.

Uses polling-based file watching that works on all platforms.
Detects file additions, deletions, modifications, and renames.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .utils import safe_stat


@dataclass
class FileEvent:
    """A detected file system event."""
    event_type: str  # "created", "deleted", "modified", "renamed"
    path: Path
    old_path: Path | None = None  # For renames
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if self.timestamp == 0:
            self.timestamp = time.time()

    @property
    def display(self) -> str:
        if self.event_type == "renamed" and self.old_path:
            return f"RENAMED {self.old_path} -> {self.path}"
        return f"{self.event_type.upper()} {self.path}"


@dataclass
class WatchState:
    """Snapshot of directory state for change detection."""
    files: dict[str, tuple[int, float]] = field(
        default_factory=dict
    )  # path_str -> (size, mtime)


class DirectoryWatcher:
    """Poll-based directory watcher.

    Periodically scans a directory and compares with the previous
    snapshot to detect changes.
    """

    def __init__(
        self,
        path: Path,
        interval: float = 2.0,
        ignore_patterns: list[str] | None = None,
    ) -> None:
        self.path = path
        self.interval = interval
        self.ignore_patterns = ignore_patterns or [
            ".git", "node_modules", "__pycache__", ".venv"
        ]
        self._state = WatchState()
        self._running = False
        self._on_event: Callable[[FileEvent], None] | None = None

    def on_event(self, callback: Callable[[FileEvent], None]) -> None:
        """Register event callback."""
        self._on_event = callback

    def _emit(self, event: FileEvent) -> None:
        if self._on_event:
            self._on_event(event)

    def _scan(self) -> WatchState:
        """Take a snapshot of current directory state."""
        state = WatchState()
        try:
            for root, dirs, files in os.walk(self.path):
                # Skip ignored directories
                dirs[:] = [
                    d for d in dirs
                    if d not in self.ignore_patterns
                ]
                for name in files:
                    filepath = Path(root) / name
                    st = safe_stat(filepath)
                    if st:
                        key = str(filepath)
                        state.files[key] = (st.st_size, st.st_mtime)
        except (PermissionError, OSError):
            pass
        return state

    def _compare(
        self, old: WatchState, new: WatchState
    ) -> list[FileEvent]:
        """Compare two snapshots and generate events."""
        events: list[FileEvent] = []
        old_keys = set(old.files.keys())
        new_keys = set(new.files.keys())

        # New files
        for key in new_keys - old_keys:
            events.append(
                FileEvent(event_type="created", path=Path(key))
            )

        # Deleted files
        for key in old_keys - new_keys:
            events.append(
                FileEvent(event_type="deleted", path=Path(key))
            )

        # Modified files
        for key in old_keys & new_keys:
            old_size, old_mtime = old.files[key]
            new_size, new_mtime = new.files[key]
            if old_mtime != new_mtime or old_size != new_size:
                events.append(
                    FileEvent(
                        event_type="modified", path=Path(key)
                    )
                )

        events.sort(key=lambda e: e.timestamp)
        return events

    def watch(self, duration: float | None = None) -> None:
        """Watch for changes.

        Args:
            duration: Watch for this many seconds, or forever if None.
        """
        self._running = True
        self._state = self._scan()
        start = time.monotonic()

        while self._running:
            time.sleep(self.interval)

            if (
                duration is not None
                and time.monotonic() - start >= duration
            ):
                break

            new_state = self._scan()
            events = self._compare(self._state, new_state)

            for event in events:
                self._emit(event)

            self._state = new_state

    def stop(self) -> None:
        """Stop watching."""
        self._running = False


def watch_directory(
    path: Path,
    interval: float = 2.0,
    duration: float | None = None,
    callback: Callable[[FileEvent], None] | None = None,
) -> DirectoryWatcher:
    """Convenience function to watch a directory.

    Returns the watcher instance (call .stop() to stop).
    """
    watcher = DirectoryWatcher(path, interval)
    if callback:
        watcher.on_event(callback)
    watcher.watch(duration)
    return watcher
