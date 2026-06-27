"""Tests for DupeClean history tracker module."""

from __future__ import annotations

from dupeclean.history_tracker import (
    HistoryRecord,
    HistoryTracker,
    format_history,
)


class TestHistoryTracker:
    def test_add(self):
        tracker = HistoryTracker()
        tracker.add(HistoryRecord(timestamp=0, operation="test", path="/a", action="delete"))
        assert tracker.total_records == 1

    def test_add_cleanup(self):
        tracker = HistoryTracker()
        tracker.add_cleanup("test", "/a", "delete", size=100)
        assert tracker.total_records == 1

    def test_success_count(self):
        tracker = HistoryTracker()
        tracker.add_cleanup("test", "/a", "delete", success=True)
        tracker.add_cleanup("test", "/b", "delete", success=False)
        assert tracker.success_count == 1

    def test_error_count(self):
        tracker = HistoryTracker()
        tracker.add_cleanup("test", "/a", "delete", success=True)
        tracker.add_cleanup("test", "/b", "delete", success=False)
        assert tracker.error_count == 1

    def test_total_size(self):
        tracker = HistoryTracker()
        tracker.add_cleanup("test", "/a", "delete", size=100, success=True)
        tracker.add_cleanup("test", "/b", "delete", size=200, success=False)
        assert tracker.total_size == 100

    def test_get_by_operation(self):
        tracker = HistoryTracker()
        tracker.add_cleanup("scan", "/a", "scan")
        tracker.add_cleanup("cleanup", "/b", "delete")
        tracker.add_cleanup("scan", "/c", "scan")
        assert len(tracker.get_by_operation("scan")) == 2

    def test_get_recent(self):
        tracker = HistoryTracker()
        for i in range(100):
            tracker.add_cleanup("test", f"/f{i}", "delete")
        recent = tracker.get_recent(10)
        assert len(recent) == 10

    def test_max_records(self):
        tracker = HistoryTracker(max_records=10)
        for i in range(20):
            tracker.add_cleanup("test", f"/f{i}", "delete")
        assert tracker.total_records <= 10

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "history.json"
        tracker = HistoryTracker()
        tracker.add_cleanup("test", "/a", "delete", size=100)
        tracker.save(path)
        assert path.exists()

        loaded = HistoryTracker.load(path)
        assert loaded.total_records == 1

    def test_load_nonexistent(self, tmp_path):
        tracker = HistoryTracker.load(tmp_path / "nope")
        assert tracker.total_records == 0


class TestHistoryRecord:
    def test_size_display(self):
        record = HistoryRecord(timestamp=0, operation="test", path="/a", action="delete", size=1024)
        assert "B" in record.size_display


class TestFormatHistory:
    def test_empty(self):
        tracker = HistoryTracker()
        assert "No history" in format_history(tracker)

    def test_with_records(self):
        tracker = HistoryTracker()
        tracker.add_cleanup("test", "/a.txt", "delete", size=100)
        text = format_history(tracker)
        assert "delete" in text
