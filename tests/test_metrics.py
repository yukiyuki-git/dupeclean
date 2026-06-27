"""Tests for DupeClean metrics module."""

from __future__ import annotations

from dupeclean.metrics import (
    Metric,
    MetricsCollector,
    format_metrics,
)


class TestMetric:
    def test_display_bytes(self):
        m = Metric(name="size", value=1024, unit="bytes")
        assert "B" in m.display

    def test_display_seconds(self):
        m = Metric(name="time", value=1.5, unit="seconds")
        assert "s" in m.display

    def test_display_percent(self):
        m = Metric(name="pct", value=75.5, unit="percent")
        assert "%" in m.display

    def test_display_default(self):
        m = Metric(name="count", value=42)
        assert m.display == "42"


class TestMetricsCollector:
    def test_record(self):
        collector = MetricsCollector()
        collector.record("test", 100, "bytes")
        assert len(collector.metrics) == 1

    def test_get(self):
        collector = MetricsCollector()
        collector.record("test", 100)
        m = collector.get("test")
        assert m is not None
        assert m.value == 100

    def test_get_nonexistent(self):
        collector = MetricsCollector()
        assert collector.get("nope") is None

    def test_get_latest(self):
        collector = MetricsCollector()
        collector.record("test", 100)
        collector.record("test", 200)
        m = collector.get("test")
        assert m is not None
        assert m.value == 200

    def test_get_all(self):
        collector = MetricsCollector()
        collector.record("test", 100)
        collector.record("test", 200)
        collector.record("other", 300)
        all_test = collector.get_all("test")
        assert len(all_test) == 2

    def test_summary(self):
        collector = MetricsCollector()
        collector.record("test", 100)
        collector.record("test", 200)
        summary = collector.summary()
        assert "test" in summary
        assert summary["test"]["count"] == 2
        assert summary["test"]["latest"] == 200


class TestFormatMetrics:
    def test_empty(self):
        collector = MetricsCollector()
        assert "No metrics" in format_metrics(collector)

    def test_with_metrics(self):
        collector = MetricsCollector()
        collector.record("scanned", 1000, "bytes")
        collector.record("time", 1.5, "seconds")
        text = format_metrics(collector)
        assert "scanned" in text
        assert "time" in text
