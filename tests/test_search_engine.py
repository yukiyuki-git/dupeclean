"""Tests for DupeClean search engine module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.search_engine import (
    SearchQuery,
    SearchResult,
    format_search_result,
    search_files,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestSearchFiles:
    def test_name_pattern(self):
        files = [_fi("/a.txt"), _fi("/b.py"), _fi("/c.txt")]
        query = SearchQuery(name_pattern="*.txt")
        result = search_files(files, query)
        assert result.count == 2

    def test_extension(self):
        files = [_fi("/a.txt"), _fi("/b.py")]
        query = SearchQuery(extension="py")
        result = search_files(files, query)
        assert result.count == 1

    def test_min_size(self):
        files = [_fi("/a", 100), _fi("/b", 1000)]
        query = SearchQuery(min_size=500)
        result = search_files(files, query)
        assert result.count == 1

    def test_max_size(self):
        files = [_fi("/a", 100), _fi("/b", 1000)]
        query = SearchQuery(max_size=500)
        result = search_files(files, query)
        assert result.count == 1

    def test_combined(self):
        files = [_fi("/a.txt", 100), _fi("/b.txt", 1000), _fi("/c.py", 200)]
        query = SearchQuery(extension="txt", min_size=500)
        result = search_files(files, query)
        assert result.count == 1

    def test_sorted_by_size(self):
        files = [_fi("/a", 100), _fi("/b", 1000), _fi("/c", 500)]
        query = SearchQuery()
        result = search_files(files, query)
        assert result.matches[0].size == 1000


class TestSearchResult:
    def test_count(self):
        result = SearchResult(query=SearchQuery(), matches=[_fi("/a"), _fi("/b")])
        assert result.count == 2

    def test_total_size(self):
        result = SearchResult(query=SearchQuery(), matches=[_fi("/a", 100), _fi("/b", 200)])
        assert result.total_size == 300


class TestFormatSearchResult:
    def test_no_matches(self):
        result = SearchResult(query=SearchQuery())
        assert "No files" in format_search_result(result)

    def test_with_matches(self):
        result = SearchResult(
            query=SearchQuery(),
            matches=[_fi("/a.txt", 1000)],
        )
        text = format_search_result(result)
        assert "1" in text
