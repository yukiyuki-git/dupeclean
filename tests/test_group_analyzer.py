"""Tests for DupeClean group analyzer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_analyzer import (
    GroupPattern,
    analyze_group_patterns,
    format_group_analysis,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int, ext: str = ".txt") -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}{ext}", size) for i in range(count)],
    )


class TestAnalyzeGroupPatterns:
    def test_basic(self):
        groups = [
            _group(0, 1000, 3, ".jpg"),
            _group(1, 2000, 2, ".jpg"),
            _group(2, 500, 4, ".txt"),
        ]
        analysis = analyze_group_patterns(groups)
        assert analysis.total_groups == 3
        assert len(analysis.patterns) > 0

    def test_empty(self):
        analysis = analyze_group_patterns([])
        assert analysis.total_groups == 0


class TestGroupAnalysisV2:
    def test_top_pattern(self):
        groups = [
            _group(0, 1000, 3, ".jpg"),
            _group(1, 100, 2, ".txt"),
        ]
        analysis = analyze_group_patterns(groups)
        top = analysis.top_pattern
        assert top is not None
        assert top.total_wasted > 0


class TestGroupPattern:
    def test_wasted_display(self):
        pattern = GroupPattern(pattern_type="test", value="test", total_wasted=1024)
        assert "B" in pattern.wasted_display


class TestFormatGroupAnalysis:
    def test_basic(self):
        groups = [_group(0, 100, 2)]
        analysis = analyze_group_patterns(groups)
        text = format_group_analysis(analysis)
        assert "Group Analysis" in text
