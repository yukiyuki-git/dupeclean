"""Tests for DupeClean group report v3 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_report_v3 import (
    GroupReportV2,
    format_report_v2,
    generate_report_v2,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestGroupReportV2:
    def test_add_summary(self):
        report = GroupReportV2()
        report.add_summary("Summary", "Content here")
        assert len(report.sections) == 1

    def test_add_table(self):
        report = GroupReportV2()
        report.add_table("Table", ["A", "B"], [["1", "2"]])
        assert len(report.sections) == 1

    def test_render(self):
        report = GroupReportV2()
        report.add_summary("Test", "Content")
        text = report.render()
        assert "DupeClean Report" in text
        assert "Test" in text

    def test_render_sorted(self):
        report = GroupReportV2()
        report.add_summary(
            "Low",
            "low",
        )
        report.add_table("High", ["A"], [["1"]])
        report.sections[1].priority = 0
        report.sections[0].priority = 2
        text = report.render()
        high_pos = text.index("High")
        low_pos = text.index("Low")
        assert high_pos < low_pos


class TestGenerateReportV2:
    def test_basic(self):
        groups = [_group(0, 1000, 3), _group(1, 2000, 2)]
        report = generate_report_v2(groups)
        text = report.render()
        assert "5" in text  # total files

    def test_empty(self):
        report = generate_report_v2([])
        text = report.render()
        assert "0" in text


class TestFormatReportV2:
    def test_basic(self):
        report = GroupReportV2()
        report.add_summary("Test", "Content")
        text = format_report_v2(report)
        assert "Test" in text
