"""Tests for DupeClean progress display module."""

from __future__ import annotations

import time

from dupeclean.progress_display import (
    ProgressDisplay,
    create_progress,
)


class TestProgressDisplay:
    def test_percentage(self):
        pd = ProgressDisplay(total=100, current=50)
        assert pd.percentage == 50.0

    def test_percentage_capped(self):
        pd = ProgressDisplay(total=100, current=150)
        assert pd.percentage == 100.0

    def test_percentage_zero(self):
        pd = ProgressDisplay(total=0, current=0)
        assert pd.percentage == 0.0

    def test_rate(self):
        pd = ProgressDisplay(total=100, current=50, start_time=time.monotonic() - 1)
        assert pd.rate > 0

    def test_eta_none_initially(self):
        pd = ProgressDisplay(total=100, current=0)
        assert pd.eta_seconds is None

    def test_render_basic(self):
        pd = ProgressDisplay(total=100, current=50, start_time=time.monotonic())
        text = pd.render()
        assert "50.0%" in text

    def test_render_with_file(self):
        pd = ProgressDisplay(total=100, current=25, file_name="test.txt")
        text = pd.render()
        assert "test.txt" in text

    def test_render_long_filename(self):
        pd = ProgressDisplay(
            total=100, current=10, file_name="very/long/path/to/some/deeply/nested/file.txt"
        )
        text = pd.render()
        assert "..." in text


class TestCreateProgress:
    def test_basic(self):
        pd = create_progress(100, "scanning")
        assert pd.total == 100
        assert pd.stage == "scanning"
        assert pd.start_time > 0
