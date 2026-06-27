"""Tests for DupeClean hybrid dedup module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.hybrid import (
    HybridDedupResult,
    analyze_hybrid,
    format_hybrid_result,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestAnalyzeHybrid:
    def test_basic(self):
        files = [
            _fi("/a/file.txt", 100),
            _fi("/b/file.txt", 100),
        ]
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=files,
            )
        ]
        result = analyze_hybrid(files, groups)
        assert result.total_groups >= 1
        assert len(result.exact_duplicates) == 1

    def test_no_duplicates(self):
        files = [
            _fi("/a.txt", 100),
            _fi("/b.txt", 200),
        ]
        result = analyze_hybrid(files, [])
        assert len(result.exact_duplicates) == 0

    def test_method_stats(self):
        files = [_fi("/a.txt", 100)]
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a", 100), _fi("/b", 100)],
            )
        ]
        result = analyze_hybrid(files, groups)
        assert "exact" in result.method_stats
        assert result.method_stats["exact"] == 1


class TestHybridDedupResult:
    def test_total_groups(self):
        result = HybridDedupResult(
            exact_duplicates=[
                DuplicateGroup(
                    group_id=0,
                    hash_value="abc",
                    file_size=100,
                    files=[_fi("/a"), _fi("/b")],
                )
            ],
        )
        assert result.total_groups == 1

    def test_savings_display(self):
        result = HybridDedupResult(total_savings=1024)
        assert "B" in result.savings_display


class TestFormatHybridResult:
    def test_basic(self):
        result = HybridDedupResult(
            exact_duplicates=[
                DuplicateGroup(
                    group_id=0,
                    hash_value="abc",
                    file_size=100,
                    files=[_fi("/a"), _fi("/b")],
                )
            ],
            method_stats={"exact": 1},
        )
        text = format_hybrid_result(result)
        assert "Hybrid" in text
        assert "exact" in text

    def test_empty(self):
        result = HybridDedupResult()
        text = format_hybrid_result(result)
        assert "0" in text
