"""Tests for DupeClean cleanup tracker module."""

from __future__ import annotations

from dupeclean.tracker import (
    CleanupTracker,
    TrackerEntry,
    format_tracker,
)


class TestCleanupTracker:
    def test_track(self):
        tracker = CleanupTracker()
        tracker.track("delete", files_count=5, space_freed=1000)
        assert tracker.total_operations == 1

    def test_total_freed(self):
        tracker = CleanupTracker()
        tracker.track("delete", space_freed=1000)
        tracker.track("hardlink", space_freed=2000)
        assert tracker.total_freed == 3000

    def test_total_files(self):
        tracker = CleanupTracker()
        tracker.track("delete", files_count=5)
        tracker.track("hardlink", files_count=3)
        assert tracker.total_files == 8

    def test_get_recent(self):
        tracker = CleanupTracker()
        for i in range(20):
            tracker.track(f"op_{i}", files_count=i)
        recent = tracker.get_recent(5)
        assert len(recent) == 5

    def test_get_by_operation(self):
        tracker = CleanupTracker()
        tracker.track("delete", files_count=5)
        tracker.track("hardlink", files_count=3)
        tracker.track("delete", files_count=2)
        assert len(tracker.get_by_operation("delete")) == 2


class TestTrackerEntry:
    def test_freed_display(self):
        entry = TrackerEntry(timestamp=0, operation="delete", space_freed=1024)
        assert "B" in entry.freed_display


class TestFormatTracker:
    def test_empty(self):
        tracker = CleanupTracker()
        assert "No tracked" in format_tracker(tracker)

    def test_with_entries(self):
        tracker = CleanupTracker()
        tracker.track("delete", files_count=5, space_freed=1000)
        text = format_tracker(tracker)
        assert "1 operations" in text
