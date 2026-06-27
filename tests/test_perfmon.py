"""Tests for DupeClean performance monitoring module."""

from __future__ import annotations

import time

from dupeclean.perfmon import (
    PerformanceMetric,
    PerformanceTracker,
    format_performance,
)


class TestPerformanceMetric:
    def test_items_per_second(self):
        m = PerformanceMetric(name="test", duration=2.0, items_processed=100)
        assert m.items_per_second == 50.0

    def test_mb_per_second(self):
        m = PerformanceMetric(
            name="test",
            duration=1.0,
            bytes_processed=1048576,
        )
        assert abs(m.mb_per_second - 1.0) < 0.01

    def test_zero_duration(self):
        m = PerformanceMetric(name="test", duration=0.0)
        assert m.items_per_second == 0.0


class TestPerformanceTracker:
    def test_start_stop(self):
        tracker = PerformanceTracker()
        tracker.start("test")
        time.sleep(0.01)
        metric = tracker.stop("test", items=100)
        assert metric.duration >= 0
        assert metric.items_processed == 100

    def test_get_metric(self):
        tracker = PerformanceTracker()
        tracker.start("test")
        tracker.stop("test", items=50)
        m = tracker.get_metric("test")
        assert m is not None
        assert m.items_processed == 50

    def test_get_metric_nonexistent(self):
        tracker = PerformanceTracker()
        assert tracker.get_metric("nope") is None

    def test_total_duration(self):
        tracker = PerformanceTracker()
        tracker.start("a")
        time.sleep(0.01)
        tracker.stop("a")
        tracker.start("b")
        time.sleep(0.01)
        tracker.stop("b")
        assert tracker.total_duration() > 0.02

    def test_summary(self):
        tracker = PerformanceTracker()
        tracker.start("test")
        tracker.stop("test", items=10)
        summary = tracker.summary()
        assert summary["total_operations"] == 1


class TestFormatPerformance:
    def test_empty(self):
        tracker = PerformanceTracker()
        assert "No performance" in format_performance(tracker)

    def test_with_metrics(self):
        tracker = PerformanceTracker()
        tracker.start("scan")
        tracker.stop("scan", items=100, bytes_count=1024)
        text = format_performance(tracker)
        assert "scan" in text
