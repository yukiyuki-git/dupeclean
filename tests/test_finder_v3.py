"""Tests for DupeClean finder v3 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.finder_v3 import (
    FinderResultV2,
    find_by_content_hash,
    find_with_prefilter,
    format_finder_result_v2,
)
from dupeclean.models import FileInfo


def _fi(
    path: str, size: int = 100, hash_val: str = ""
) -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    if hash_val:
        fi.quick_hash = hash_val
    return fi


class TestFindWithPrefilter:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 100), _fi("/c", 200)]
        result = find_with_prefilter(files)
        assert result.count >= 1
        assert result.method == "prefilter"

    def test_no_duplicates(self):
        files = [_fi("/a", 100), _fi("/b", 200), _fi("/c", 300)]
        result = find_with_prefilter(files)
        assert result.count == 0

    def test_candidates_filtered(self):
        files = [_fi("/a", 100), _fi("/b", 100), _fi("/c", 200)]
        result = find_with_prefilter(files)
        assert result.candidates_filtered == 2


class TestFindByContentHash:
    def test_basic(self):
        files = [_fi("/a", 100, "h1"), _fi("/b", 100, "h1")]
        result = find_by_content_hash(files)
        assert result.count == 1

    def test_no_hash(self):
        files = [_fi("/a", 100), _fi("/b", 100)]
        result = find_by_content_hash(files)
        assert result.count == 0


class TestFinderResultV2:
    def test_total_duplicates(self):
        result = FinderResultV2()
        assert result.total_duplicates == 0

    def test_wasted_display(self):
        result = FinderResultV2()
        assert "B" in result.wasted_display

    def test_filter_ratio(self):
        result = FinderResultV2(files_scanned=100, candidates_filtered=20)
        assert result.filter_ratio == 0.2


class TestFormatFinderResultV2:
    def test_basic(self):
        result = FinderResultV2(method="test", files_scanned=100)
        text = format_finder_result_v2(result)
        assert "test" in text
        assert "100" in text
