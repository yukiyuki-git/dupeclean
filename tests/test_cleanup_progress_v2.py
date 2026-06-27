"""Tests for DupeClean cleanup progress v2 module."""

from __future__ import annotations

import time

from dupeclean.cleanup_progress_v2 import (
    ProgressMetricsV2,
    create_progress_v2,
)


class TestProgressMetricsV2:
    def test_group_percentage(self):
        metrics = ProgressMetricsV2(total_groups=100, groups_processed=50)
        assert metrics.group_percentage == 50.0

    def test_update_group(self):
        metrics = ProgressMetricsV2(total_groups=100)
        metrics.update_group()
        assert metrics.groups_processed == 1

    def test_update_file(self):
        metrics = ProgressMetricsV2(total_files=100)
        metrics.update_file(deleted=True, freed=1000)
        assert metrics.files_processed == 1
        assert metrics.files_deleted == 1
        assert metrics.bytes_freed == 1000

    def test_freed_display(self):
        metrics = ProgressMetricsV2(bytes_freed=1024)
        assert "B" in metrics.freed_display

    def test_eta_none(self):
        metrics = ProgressMetricsV2(total_groups=100)
        assert metrics.eta is None

    def test_render(self):
        metrics = ProgressMetricsV2(
            total_groups=100,
            groups_processed=50,
            start_time=time.monotonic(),
        )
        text = metrics.render()
        assert "50.0%" in text


class TestCreateProgressV2:
    def test_basic(self):
        progress = create_progress_v2(100, 500)
        assert progress.total_groups == 100
        assert progress.total_files == 500
