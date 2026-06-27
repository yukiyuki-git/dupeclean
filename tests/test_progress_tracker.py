"""Tests for DupeClean progress tracking module."""

from __future__ import annotations

from dupeclean.progress_tracker import (
    ProgressTracker,
    format_progress,
)


class TestProgressTracker:
    def test_start(self):
        tracker = ProgressTracker()
        tracker.start(100, "scanning")
        assert tracker.total == 100
        assert tracker.stage == "scanning"

    def test_update(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.update(50)
        assert tracker.current == 50

    def test_set(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.set(75)
        assert tracker.current == 75

    def test_percentage(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.set(50)
        assert tracker.percentage == 50.0

    def test_percentage_capped(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.set(150)
        assert tracker.percentage == 100.0

    def test_is_complete(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.set(100)
        assert tracker.is_complete is True

    def test_is_not_complete(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.set(50)
        assert tracker.is_complete is False

    def test_eta_none_initially(self):
        tracker = ProgressTracker()
        tracker.start(100)
        assert tracker.eta is None

    def test_rate(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.set(50)
        # Rate depends on elapsed time
        assert tracker.rate >= 0


class TestFormatProgress:
    def test_basic(self):
        tracker = ProgressTracker()
        tracker.start(100)
        tracker.set(50)
        text = format_progress(tracker)
        assert "50.0%" in text

    def test_with_stage(self):
        tracker = ProgressTracker()
        tracker.start(100, "hashing")
        tracker.set(25)
        text = format_progress(tracker)
        assert "hashing" in text

    def test_zero_total(self):
        tracker = ProgressTracker()
        tracker.start(0)
        text = format_progress(tracker)
        assert "0.0%" in text
