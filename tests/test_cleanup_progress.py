"""Tests for DupeClean cleanup progress module."""

from __future__ import annotations

import time

from dupeclean.cleanup_progress import (
    ProgressMetrics,
    create_progress,
)


class TestProgressMetrics:
    def test_percentage(self):
        metrics = ProgressMetrics(files_total=100, files_processed=50)
        assert metrics.percentage == 50.0

    def test_percentage_capped(self):
        metrics = ProgressMetrics(files_total=100, files_processed=150)
        assert metrics.percentage == 100.0

    def test_update(self):
        metrics = ProgressMetrics(files_total=100)
        metrics.update(count=1, bytes_count=1024, success=True)
        assert metrics.files_processed == 1
        assert metrics.bytes_processed == 1024
        assert metrics.files_succeeded == 1

    def test_update_failure(self):
        metrics = ProgressMetrics(files_total=100)
        metrics.update(count=1, success=False)
        assert metrics.files_failed == 1

    def test_success_rate(self):
        metrics = ProgressMetrics(files_processed=10, files_succeeded=8)
        assert metrics.success_rate == 0.8

    def test_zero_processed(self):
        metrics = ProgressMetrics()
        assert metrics.success_rate == 0.0

    def test_rate(self):
        metrics = ProgressMetrics(files_processed=50, start_time=time.monotonic() - 1)
        assert metrics.rate > 0

    def test_eta_none(self):
        metrics = ProgressMetrics(files_total=100, files_processed=0)
        assert metrics.eta is None

    def test_bytes_display(self):
        metrics = ProgressMetrics(bytes_processed=1024)
        assert "B" in metrics.bytes_display

    def test_render(self):
        metrics = ProgressMetrics(files_total=100, files_processed=50, start_time=time.monotonic())
        text = metrics.render()
        assert "50.0%" in text


class TestCreateProgress:
    def test_basic(self):
        metrics = create_progress(100, 10000)
        assert metrics.files_total == 100
        assert metrics.bytes_total == 10000
        assert metrics.start_time > 0
