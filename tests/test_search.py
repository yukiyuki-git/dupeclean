"""Tests for DupeClean file search module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dupeclean.models import FileInfo
from dupeclean.search import (
    SearchQuery,
    SearchResult,
    format_search_result,
    search_by_extension,
    search_by_name,
    search_by_size,
    search_files,
)


def _fi(path: str, size: int) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


@pytest.fixture
def sample_files():
    return [
        _fi("/test/photo.jpg", 5000),
        _fi("/test/image.PNG", 8000),
        _fi("/test/document.pdf", 50000),
        _fi("/test/report.pdf", 100000),
        _fi("/test/code.py", 2000),
        _fi("/test/readme.md", 500),
        _fi("/test/data.csv", 10000),
        _fi("/test/archive.zip", 500000),
    ]


class TestSearchFiles:
    def test_name_pattern_glob(self, sample_files):
        query = SearchQuery(name_pattern="*.pdf")
        result = search_files(sample_files, query)
        assert result.count == 2

    def test_name_pattern_regex(self, sample_files):
        query = SearchQuery(name_pattern=r"report|document")
        result = search_files(sample_files, query)
        assert result.count == 2

    def test_extension_filter(self, sample_files):
        query = SearchQuery(extension="pdf")
        result = search_files(sample_files, query)
        assert result.count == 2

    def test_min_size(self, sample_files):
        query = SearchQuery(min_size=50000)
        result = search_files(sample_files, query)
        assert all(f.size >= 50000 for f in result.matches)

    def test_max_size(self, sample_files):
        query = SearchQuery(max_size=5000)
        result = search_files(sample_files, query)
        assert all(f.size <= 5000 for f in result.matches)

    def test_size_range(self, sample_files):
        query = SearchQuery(min_size=5000, max_size=50000)
        result = search_files(sample_files, query)
        for fi in result.matches:
            assert 5000 <= fi.size <= 50000

    def test_combined_filters(self, sample_files):
        query = SearchQuery(extension="pdf", min_size=100001)
        result = search_files(sample_files, query)
        assert result.count == 0

    def test_no_matches(self, sample_files):
        query = SearchQuery(name_pattern="*.xyz")
        result = search_files(sample_files, query)
        assert result.count == 0

    def test_sorted_by_size(self, sample_files):
        query = SearchQuery()
        result = search_files(sample_files, query)
        sizes = [f.size for f in result.matches]
        assert sizes == sorted(sizes, reverse=True)


class TestSearchByName:
    def test_basic(self, sample_files):
        result = search_by_name(sample_files, "*.py")
        assert result.count == 1
        assert result.matches[0].path.name == "code.py"


class TestSearchByExtension:
    def test_basic(self, sample_files):
        result = search_by_extension(sample_files, "pdf")
        assert result.count == 2


class TestSearchBySize:
    def test_large_files(self, sample_files):
        result = search_by_size(sample_files, min_size=200000)
        assert result.count == 1
        assert result.matches[0].path.name == "archive.zip"


class TestSearchResult:
    def test_count(self):
        result = SearchResult(
            query=SearchQuery(),
            matches=[_fi("/a", 100), _fi("/b", 200)],
        )
        assert result.count == 2

    def test_total_size(self):
        result = SearchResult(
            query=SearchQuery(),
            matches=[_fi("/a", 100), _fi("/b", 200)],
        )
        assert result.total_size == 300


class TestFormatSearchResult:
    def test_empty_result(self):
        result = SearchResult(query=SearchQuery())
        text = format_search_result(result)
        assert "No files found" in text

    def test_with_results(self, sample_files):
        result = search_by_extension(sample_files, "pdf")
        text = format_search_result(result)
        assert "2 files" in text or "2" in text
