"""Tests for DupeClean file locking module."""

from __future__ import annotations

from dupeclean.locking import (
    FileLock,
    LockInfo,
    format_lock_info,
)


class TestFileLock:
    def test_acquire_and_release(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock = FileLock(lock_path)
        assert lock.acquire() is True
        assert lock.is_locked is True
        lock.release()
        assert lock.is_locked is False

    def test_double_acquire(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock1 = FileLock(lock_path)
        lock2 = FileLock(lock_path)
        assert lock1.acquire(timeout=1) is True
        assert lock2.acquire(timeout=0.5) is False
        lock1.release()
        assert lock2.acquire(timeout=1) is True
        lock2.release()

    def test_context_manager(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        with FileLock(lock_path) as lock:
            assert lock.is_locked is True
        assert lock_path.exists() is False

    def test_stale_lock(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        import json

        # Create a stale lock (old timestamp)
        lock_path.write_text(
            json.dumps({
                "pid": 99999,
                "timestamp": 0,
                "operation": "old",
                "path": str(tmp_path),
            })
        )
        lock = FileLock(lock_path)
        assert lock._is_stale() is True

    def test_get_lock_info(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock = FileLock(lock_path)
        lock.acquire(operation="test_scan")
        info = lock.get_lock_info()
        assert info is not None
        assert info.operation == "test_scan"
        lock.release()

    def test_get_lock_info_no_lock(self, tmp_path):
        lock_path = tmp_path / "test.lock"
        lock = FileLock(lock_path)
        assert lock.get_lock_info() is None


class TestFormatLockInfo:
    def test_no_lock(self):
        assert "No active" in format_lock_info(None)

    def test_with_lock(self):
        info = LockInfo(
            pid=12345,
            timestamp=1000000,
            operation="scan",
            path="/test",
        )
        text = format_lock_info(info)
        assert "12345" in text
        assert "scan" in text
