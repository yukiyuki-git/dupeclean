"""Tests for DupeClean dedup report module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_report import (
    DedupReport,
    format_groups_table,
    generate_dedup_report,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _make_groups() -> list[DuplicateGroup]:
    return [
        DuplicateGroup(
            group_id=0,
            hash_value="abc123",
            file_size=1000,
            files=[_fi("/a"), _fi("/b"), _fi("/c")],
        ),
        DuplicateGroup(
            group_id=1,
            hash_value="def456",
            file_size=2000,
            files=[_fi("/d"), _fi("/e")],
        ),
    ]


class TestDedupReport:
    def test_add_section(self):
        report = DedupReport(title="Test")
        report.add_section("Section 1", "Content 1")
        assert len(report.sections) == 1

    def test_render(self):
        report = DedupReport(title="Test Report")
        report.add_section("Section", "Content here")
        text = report.render()
        assert "Test Report" in text
        assert "Section" in text
        assert "Content here" in text

    def test_render_sorted_by_priority(self):
        report = DedupReport(title="Test")
        report.add_section("Low", "low", priority=2)
        report.add_section("High", "high", priority=0)
        text = report.render()
        high_pos = text.index("High")
        low_pos = text.index("Low")
        assert high_pos < low_pos


class TestGenerateDedupReport:
    def test_basic(self):
        groups = _make_groups()
        report = generate_dedup_report(groups)
        text = report.render()
        assert "DupeClean" in text
        assert "duplicate" in text.lower()

    def test_with_totals(self):
        groups = _make_groups()
        report = generate_dedup_report(groups, total_files=100, total_size=100000)
        text = report.render()
        assert "%" in text

    def test_empty_groups(self):
        report = generate_dedup_report([])
        text = report.render()
        assert "0" in text


class TestFormatGroupsTable:
    def test_basic(self):
        groups = _make_groups()
        text = format_groups_table(groups)
        assert "Group" in text or "#" in text
        assert "abc123" in text or "Files" in text

    def test_empty(self):
        assert "No duplicate" in format_groups_table([])

    def test_many_groups(self):
        groups = [
            DuplicateGroup(
                group_id=i,
                hash_value=f"h{i}",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
            for i in range(50)
        ]
        text = format_groups_table(groups)
        assert "more" in text
