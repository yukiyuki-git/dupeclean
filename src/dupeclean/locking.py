"""File locking module for DupeClean.

Prevent concurrent modifications during cleanup operations.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

LOCK_FILE = ".dupeclean.lock"


@dataclass
class LockInfo:
    """Lock information."""

    pid: int
    timestamp: float
    operation: str
    path: str


class FileLock:
    """File-based lock for preventing concurrent operations."""

    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self._locked = False

    def acquire(self, operation: str = "scan", timeout: float = 30.0) -> bool:
        """Acquire the lock.

        Args:
            operation: Description of the operation.
            timeout: Max seconds to wait for lock.

        Returns:
            True if lock acquired.
        """
        start = time.monotonic()

        while True:
            if self._try_acquire(operation):
                self._locked = True
                return True

            # Check for stale lock
            if self._is_stale():
                self.release()

            if time.monotonic() - start >= timeout:
                return False

            time.sleep(0.1)

    def release(self) -> None:
        """Release the lock."""
        import contextlib

        with contextlib.suppress(OSError):
            self.lock_path.unlink(missing_ok=True)
        self._locked = False

    def _try_acquire(self, operation: str) -> bool:
        """Try to create the lock file."""
        if self.lock_path.exists():
            return False

        try:
            lock_info = LockInfo(
                pid=os.getpid(),
                timestamp=time.time(),
                operation=operation,
                path=str(self.lock_path.parent),
            )
            self.lock_path.write_text(
                json.dumps(
                    {
                        "pid": lock_info.pid,
                        "timestamp": lock_info.timestamp,
                        "operation": lock_info.operation,
                        "path": lock_info.path,
                    }
                ),
                encoding="utf-8",
            )
            return True
        except OSError:
            return False

    def _is_stale(self, max_age: float = 300) -> bool:
        """Check if existing lock is stale (older than max_age)."""
        if not self.lock_path.exists():
            return False

        try:
            data = json.loads(self.lock_path.read_text(encoding="utf-8"))
            lock_time = data.get("timestamp", 0)
            return (time.time() - lock_time) > max_age
        except (json.JSONDecodeError, OSError):
            return True

    @property
    def is_locked(self) -> bool:
        return self.lock_path.exists()

    def get_lock_info(self) -> LockInfo | None:
        """Get information about the current lock."""
        if not self.lock_path.exists():
            return None

        try:
            data = json.loads(self.lock_path.read_text(encoding="utf-8"))
            return LockInfo(
                pid=data["pid"],
                timestamp=data["timestamp"],
                operation=data["operation"],
                path=data["path"],
            )
        except (json.JSONDecodeError, OSError, KeyError):
            return None

    def __enter__(self) -> FileLock:
        self.acquire()
        return self

    def __exit__(self, *args) -> None:
        self.release()


def format_lock_info(info: LockInfo | None) -> str:
    """Format lock information as text."""
    if info is None:
        return "No active lock."

    import datetime

    dt = datetime.datetime.fromtimestamp(info.timestamp)
    return (
        f"Lock held by PID {info.pid}\n"
        f"  Operation: {info.operation}\n"
        f"  Since: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
    )
