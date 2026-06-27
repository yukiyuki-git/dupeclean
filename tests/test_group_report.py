"""Tests for DupeClean group report module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_report import (
    GroupReport,
    format_group_report,
    generate_group_report,
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


class TestGroupReport:
    def test_add_section(self):
        report = GroupReport()
        report.add_section("Test", "Content")
        assert len(report.sections) == 1

    def test_render_empty(self):
        report = GroupReport()
        text = report.render()
        assert "Group Report" in text

    def test_render_with_sections(self):
        report = GroupReport()
        report.add_section("Section 1", "Content 1")
        report.add_section("Section 2", "Content 2")
        text = report.render()
        assert "Section 1" in text
        assert "Section 2" in text

    def test_priority_sorting(self):
        report = GroupReport()
        report.add_section("Low", "low", priority=2)
        report.add_section("High", "high", priority=0)
        assert report.sections[0].title == "High"


class TestGenerateGroupReport:
    def test_basic(self):
        groups = [_group(0, 1000, 3), _group(1, 2000, 2)]
        report = generate_group_report(groups)
        text = report.render()
        assert "Groups:" in text
        assert "5" in text  # total files

    def test_empty(self):
        report = generate_group_report([])
        text = report.render()
        assert "0" in text


class TestFormatGroupReport:
    def test_basic(self):
        report = GroupReport()
        report.add_section("Test", "Content")
        text = format_group_report(report)
        assert "Test" in text
