"""Tests for DupeClean dedup reporting v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_report_v2 import (
    DedupReportV2,
    format_report,
    generate_full_report,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _make_groups() -> list[DuplicateGroup]:
    return [
        DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=1000,
            files=[_fi("/a"), _fi("/b"), _fi("/c")],
        ),
        DuplicateGroup(
            group_id=1,
            hash_value="def",
            file_size=2000,
            files=[_fi("/d"), _fi("/e")],
        ),
    ]


class TestDedupReportV2:
    def test_add_text(self):
        report = DedupReportV2(title="Test")
        report.add_text("Section", "Content here")
        assert len(report.sections) == 1

    def test_add_table(self):
        report = DedupReportV2(title="Test")
        report.add_table(
            "Table",
            ["Name", "Size"],
            [["file.txt", "100"]],
        )
        assert len(report.sections) == 1

    def test_render(self):
        report = DedupReportV2(title="Test Report")
        report.add_text("Section", "Content")
        text = report.render()
        assert "Test Report" in text
        assert "Section" in text
        assert "Content" in text


class TestGenerateFullReport:
    def test_basic(self):
        groups = _make_groups()
        report = generate_full_report(groups, 100, 100000)
        text = report.render()
        assert "DupeClean" in text
        assert "Summary" in text

    def test_with_table(self):
        groups = _make_groups()
        report = generate_full_report(groups)
        text = report.render()
        assert "Top Duplicate" in text

    def test_empty_groups(self):
        report = generate_full_report([])
        text = report.render()
        assert "0" in text


class TestFormatReport:
    def test_basic(self):
        report = DedupReportV2(title="Test")
        report.add_text("Section", "Content")
        text = format_report(report)
        assert "Test" in text
