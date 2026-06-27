"""Tests for DupeClean smart suggestions module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.analyzer import AnalysisResult
from dupeclean.models import (
    DirInfo,
    DuplicateGroup,
    FileInfo,
    ScanStats,
)
from dupeclean.suggestions import (
    Suggestion,
    format_suggestions,
    generate_suggestions,
)


def _make_result(
    files: list[FileInfo],
    duplicates: list[DuplicateGroup] | None = None,
) -> AnalysisResult:
    """Create a minimal AnalysisResult for testing."""
    dirs = {
        Path("/"): DirInfo(
            path=Path("/"),
            total_size=sum(f.size for f in files),
            file_count=len(files),
        )
    }
    stats = ScanStats(
        total_files=len(files),
        total_size=sum(f.size for f in files),
    )
    return AnalysisResult(
        root=Path("/"),
        files=files,
        dirs=dirs,
        stats=stats,
        duplicates=duplicates or [],
    )


def _fi(path: str, size: int, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestGenerateSuggestions:
    def test_with_duplicates(self):
        files = [
            _fi("/a.txt", 1000),
            _fi("/b.txt", 1000),
        ]
        dup_group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=1000,
            files=files,
        )
        result = _make_result(files, [dup_group])
        suggestions = generate_suggestions(result)

        assert len(suggestions) >= 1
        assert any(s.category == "cleanup" for s in suggestions)

    def test_with_large_files(self):
        files = [_fi("/big.bin", 200_000_000)]
        result = _make_result(files)
        suggestions = generate_suggestions(result)

        large = [s for s in suggestions if "large" in s.title.lower()]
        assert len(large) >= 1

    def test_with_old_files(self):
        old_time = time.time() - (400 * 86400)
        files = [_fi(f"/old_{i}.txt", 1000, mtime=old_time) for i in range(15)]
        result = _make_result(files)
        suggestions = generate_suggestions(result)

        old = [s for s in suggestions if "old" in s.title.lower()]
        assert len(old) >= 1

    def test_with_empty_files(self):
        files = [_fi("/empty.txt", 0)]
        result = _make_result(files)
        suggestions = generate_suggestions(result)

        empty = [s for s in suggestions if "empty" in s.title.lower()]
        assert len(empty) >= 1

    def test_no_suggestions_for_clean_dir(self):
        files = [_fi("/small.txt", 100)]
        result = _make_result(files)
        suggestions = generate_suggestions(result)

        # Should have few or no suggestions
        assert isinstance(suggestions, list)

    def test_sorted_by_priority(self):
        files = [
            _fi("/a.txt", 1000),
            _fi("/b.txt", 1000),
            _fi("/empty.txt", 0),
            _fi("/big.bin", 200_000_000),
        ]
        dup_group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=1000,
            files=[files[0], files[1]],
        )
        result = _make_result(files, [dup_group])
        suggestions = generate_suggestions(result)

        for i in range(len(suggestions) - 1):
            assert suggestions[i].priority <= suggestions[i + 1].priority


class TestSuggestion:
    def test_savings_display(self):
        s = Suggestion(
            priority=1,
            category="cleanup",
            title="Test",
            description="Test",
            estimated_savings=1024,
        )
        assert "B" in s.savings_display

    def test_zero_savings(self):
        s = Suggestion(
            priority=1,
            category="cleanup",
            title="Test",
            description="Test",
            estimated_savings=0,
        )
        assert s.savings_display == "0 B"


class TestFormatSuggestions:
    def test_empty_suggestions(self):
        text = format_suggestions([])
        assert "No suggestions" in text

    def test_contains_categories(self):
        suggestions = [
            Suggestion(
                priority=1,
                category="cleanup",
                title="Remove dupes",
                description="Remove duplicate files",
                estimated_savings=1000,
            ),
        ]
        text = format_suggestions(suggestions)
        assert "CLEANUP" in text
        assert "Remove dupes" in text

    def test_shows_total_savings(self):
        suggestions = [
            Suggestion(
                priority=1,
                category="cleanup",
                title="A",
                description="A",
                estimated_savings=1000,
            ),
            Suggestion(
                priority=2,
                category="compress",
                title="B",
                description="B",
                estimated_savings=2000,
            ),
        ]
        text = format_suggestions(suggestions)
        assert "Total potential savings" in text
