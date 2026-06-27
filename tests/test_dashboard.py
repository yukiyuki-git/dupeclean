"""Tests for DupeClean dashboard module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dashboard import (
    Dashboard,
    create_dashboard,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestDashboard:
    def test_add_metric(self):
        d = Dashboard(title="Test")
        d.add_metric("Files", "100", "total files")
        assert len(d.widgets) == 1
        assert d.widgets[0].widget_type == "metric"

    def test_add_gauge(self):
        d = Dashboard(title="Test")
        d.add_gauge("Usage", 75.0)
        assert len(d.widgets) == 1
        assert d.widgets[0].widget_type == "gauge"

    def test_add_chart(self):
        d = Dashboard(title="Test")
        d.add_chart("Sizes", ["a", "b"], [10, 20])
        assert len(d.widgets) == 1
        assert d.widgets[0].widget_type == "chart"

    def test_add_table(self):
        d = Dashboard(title="Test")
        d.add_table("Files", ["Name", "Size"], [["a.txt", "100"]])
        assert len(d.widgets) == 1
        assert d.widgets[0].widget_type == "table"

    def test_render_metric(self):
        d = Dashboard(title="Test")
        d.add_metric("Count", "42")
        text = d.render()
        assert "Count" in text
        assert "42" in text

    def test_render_gauge(self):
        d = Dashboard(title="Test")
        d.add_gauge("Usage", 50.0)
        text = d.render()
        assert "Usage" in text
        assert "█" in text

    def test_render_chart(self):
        d = Dashboard(title="Test")
        d.add_chart("Chart", ["a", "b"], [10, 20])
        text = d.render()
        assert "Chart" in text
        assert "a" in text

    def test_render_table(self):
        d = Dashboard(title="Test")
        d.add_table("Table", ["Name", "Size"], [["a", "100"]])
        text = d.render()
        assert "Table" in text


class TestCreateDashboard:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/c")],
            )
        ]
        dashboard = create_dashboard(files, groups)
        assert dashboard.title == "DupeClean Dashboard"
        assert len(dashboard.widgets) > 0

    def test_empty(self):
        dashboard = create_dashboard([], [])
        assert len(dashboard.widgets) > 0
