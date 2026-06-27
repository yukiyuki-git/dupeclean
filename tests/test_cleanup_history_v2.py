"""Tests for DupeClean cleanup history v2 module."""

from __future__ import annotations

import pytest

from dupeclean.cleanup_history_v2 import (
    CleanupHistoryV2,
    CleanupRecord,
    format_cleanup_history_v2,
)


@pytest.fixture
def history():
    return CleanupHistoryV2()


class TestCleanupHistoryV2:
    def test_add(self, history):
        history.add(CleanupRecord(timestamp=1000, operation="delete", files_affected=5))
        assert history.total_operations == 1

    def test_add_cleanup(self, history):
        history.add_cleanup("delete", 5, 1000)
        assert history.total_operations == 1
        assert history.total_freed == 1000

    def test_total_freed(self, history):
        history.add_cleanup("delete", 5, 1000)
        history.add_cleanup("hardlink", 3, 2000)
        assert history.total_freed == 3000

    def test_success_count(self, history):
        history.add_cleanup("delete", 5, 1000, success=True)
        history.add_cleanup("delete", 3, 0, success=False)
        assert history.success_count == 1

    def test_save_and_load(self, tmp_path, history):
        path = tmp_path / "history.json"
        history.add_cleanup("delete", 5, 1000)
        history.save(path)
        assert path.exists()

        loaded = CleanupHistoryV2.load(path)
        assert loaded.total_operations == 1

    def test_load_nonexistent(self, tmp_path):
        history = CleanupHistoryV2.load(tmp_path / "nope")
        assert history.total_operations == 0


class TestCleanupRecord:
    def test_freed_display(self):
        record = CleanupRecord(timestamp=0, operation="test", space_freed=1024)
        assert "B" in record.freed_display


class TestFormatCleanupHistoryV2:
    def test_empty(self, history):
        assert "No cleanup" in format_cleanup_history_v2(history)

    def test_with_records(self, history):
        history.add_cleanup("delete", 5, 1000)
        text = format_cleanup_history_v2(history)
        assert "delete" in text
