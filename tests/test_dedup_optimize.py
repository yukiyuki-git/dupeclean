"""Tests for DupeClean dedup optimization strategies."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_optimize import (
    OptimizationSuggestion,
    format_suggestions,
    suggest_optimizations,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestSuggestOptimizations:
    def test_many_small_files(self):
        files = [_fi(f"/small_{i}", 100) for i in range(2000)]
        suggestions = suggest_optimizations(files)
        names = [s.name for s in suggestions]
        assert "batch_small_files" in names

    def test_unique_sizes(self):
        files = [_fi(f"/f{i}", (i + 1) * 1000) for i in range(100)]
        suggestions = suggest_optimizations(files)
        names = [s.name for s in suggestions]
        assert "skip_hashing" in names

    def test_large_files(self):
        files = [
            _fi("/big.bin", 200_000_000),
            _fi("/small.txt", 100),
        ]
        suggestions = suggest_optimizations(files)
        names = [s.name for s in suggestions]
        assert "parallel_large_files" in names

    def test_dominant_extension(self):
        files = [_fi(f"/f{i}.py", 1000) for i in range(100)]
        files.append(_fi("/a.txt", 100))
        suggestions = suggest_optimizations(files)
        names = [s.name for s in suggestions]
        assert "group_by_extension" in names

    def test_empty(self):
        suggestions = suggest_optimizations([])
        assert len(suggestions) == 0

    def test_sorted_by_priority(self):
        files = [_fi(f"/f{i}", 100) for i in range(2000)]
        suggestions = suggest_optimizations(files)
        for i in range(len(suggestions) - 1):
            assert suggestions[i].priority <= suggestions[i + 1].priority


class TestOptimizationSuggestion:
    def test_defaults(self):
        s = OptimizationSuggestion(name="test", description="test desc")
        assert s.estimated_speedup == 1.0


class TestFormatSuggestions:
    def test_empty(self):
        assert "No optimization" in format_suggestions([])

    def test_with_suggestions(self):
        suggestions = [
            OptimizationSuggestion(
                name="test",
                description="Test suggestion",
                estimated_speedup=2.0,
            )
        ]
        text = format_suggestions(suggestions)
        assert "test" in text
        assert "2.0x" in text
