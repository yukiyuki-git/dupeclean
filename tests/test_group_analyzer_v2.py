"""Tests for DupeClean group analyzer v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_analyzer_v2 import (
    GroupAnalysisResult,
    GroupInsight,
    analyze_group_patterns,
    format_group_insights,
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
        result = analyze_group_patterns(groups)
        assert ".jpg" in result.patterns
        assert ".txt" in result.patterns

    def test_empty(self):
        result = analyze_group_patterns([])
        assert result.insight_count == 0

    def test_large_group_insight(self):
        groups = [_group(0, 100, 15)]
        result = analyze_group_patterns(groups)
        assert any("Large" in i.title for i in result.insights)

    def test_high_waste_insight(self):
        groups = [_group(0, 50_000_000, 5)]
        result = analyze_group_patterns(groups)
        assert any("High waste" in i.title for i in result.insights)


class TestGroupAnalysisResult:
    def test_has_insights(self):
        result = GroupAnalysisResult(insights=[
            GroupInsight(group_id=0, insight_type="test", title="test", description="test")
        ])
        assert result.has_insights is True


class TestFormatGroupInsights:
    def test_empty(self):
        result = GroupAnalysisResult()
        assert "No insights" in format_group_insights(result)

    def test_with_insights(self):
        result = GroupAnalysisResult(insights=[
            GroupInsight(group_id=0, insight_type="test", title="Test insight", description="Details")
        ])
        text = format_group_insights(result)
        assert "Test insight" in text
