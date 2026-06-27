"""Tests for DupeClean group analyzer v3 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_analyzer_v3 import (
    AnalysisV3Result,
    Pattern,
    analyze_advanced,
    format_analysis_v3,
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


class TestAnalyzeAdvanced:
    def test_basic(self):
        groups = [_group(0, 1000, 3, ".jpg"), _group(1, 2000, 2, ".jpg")]
        result = analyze_advanced(groups)
        assert isinstance(result, AnalysisV3Result)

    def test_empty(self):
        result = analyze_advanced([])
        assert result.pattern_count == 0

    def test_high_duplication(self):
        groups = [_group(0, 100, 10)]
        result = analyze_advanced(groups)
        assert any("high_duplication" in p.pattern_type for p in result.patterns)

    def test_recommendations(self):
        # Many groups to trigger recommendation
        groups = [_group(i, 100, 2) for i in range(150)]
        result = analyze_advanced(groups)
        assert len(result.recommendations) > 0


class TestAnalysisV3Result:
    def test_pattern_count(self):
        result = AnalysisV3Result(patterns=[Pattern(pattern_type="test", description="test")])
        assert result.pattern_count == 1


class TestFormatAnalysisV3:
    def test_empty(self):
        result = AnalysisV3Result()
        text = format_analysis_v3(result)
        assert "0 patterns" in text

    def test_with_patterns(self):
        result = AnalysisV3Result(
            patterns=[Pattern(pattern_type="test", description="Test pattern", frequency=5)]
        )
        text = format_analysis_v3(result)
        assert "Test pattern" in text
