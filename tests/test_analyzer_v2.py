"""Tests for DupeClean enhanced analyzer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.analyzer_v2 import (
    AnalysisV2Result,
    analyze_v2,
    format_analysis_v2,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestAnalyzeV2:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 100), _fi("/c", 200)]
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        result = analyze_v2(files, groups)
        assert result.total_files == 3
        assert result.hash_groups == 1

    def test_no_duplicates(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        result = analyze_v2(files, [])
        assert result.total_duplicates == 0

    def test_size_groups(self):
        files = [_fi("/a", 100), _fi("/b", 100), _fi("/c", 200)]
        result = analyze_v2(files, [])
        assert result.size_groups == 1


class TestAnalysisV2Result:
    def test_waste_pct(self):
        result = AnalysisV2Result(total_size=1000, total_wasted=200)
        assert result.waste_pct == 20.0

    def test_dupe_pct(self):
        result = AnalysisV2Result(total_files=100, total_duplicates=25)
        assert result.dupe_pct == 25.0

    def test_zero_totals(self):
        result = AnalysisV2Result()
        assert result.waste_pct == 0.0
        assert result.dupe_pct == 0.0


class TestFormatAnalysisV2:
    def test_basic(self):
        result = AnalysisV2Result(total_files=100, total_size=10000)
        text = format_analysis_v2(result)
        assert "100" in text
        assert "Enhanced" in text
