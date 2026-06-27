"""Tests for DupeClean duplicate analyzer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.duplicate_analyzer import (
    DuplicateAnalysis,
    GroupAnalysis,
    analyze_duplicates,
    format_analysis,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestAnalyzeDuplicates:
    def test_basic(self):
        groups = [
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
        analysis = analyze_duplicates(groups)
        assert analysis.total_groups == 2
        assert analysis.total_files == 5
        assert analysis.total_wasted == 4000  # 2000 + 2000

    def test_empty(self):
        analysis = analyze_duplicates([])
        assert analysis.total_groups == 0


class TestDuplicateAnalysis:
    def test_wasted_display(self):
        analysis = DuplicateAnalysis(total_wasted=1024)
        assert "B" in analysis.wasted_display


class TestFormatAnalysis:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        analysis = analyze_duplicates(groups)
        text = format_analysis(analysis)
        assert "Groups:" in text
        assert "Files:" in text


class TestGroupAnalysis:
    def test_defaults(self):
        analysis = GroupAnalysis(group_id=0, file_count=2, file_size=100, wasted_space=100)
        assert analysis.extensions == []
