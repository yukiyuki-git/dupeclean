"""Tests for DupeClean group filter module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_filter import (
    chain_filters,
    filter_by_extension,
    filter_by_max_size,
    filter_by_min_count,
    filter_by_min_size,
    filter_by_min_waste,
    filter_by_pattern,
    format_filter_result,
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


class TestFilterByMinCount:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 100, 5)]
        filtered = filter_by_min_count(groups, 3)
        assert len(filtered) == 1
        assert filtered[0].count == 5


class TestFilterByMinSize:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 1000, 2)]
        filtered = filter_by_min_size(groups, 500)
        assert len(filtered) == 1


class TestFilterByMaxSize:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 1000, 2)]
        filtered = filter_by_max_size(groups, 500)
        assert len(filtered) == 1


class TestFilterByExtension:
    def test_basic(self):
        groups = [_group(0, 100, 2, ".txt"), _group(1, 100, 2, ".py")]
        filtered = filter_by_extension(groups, ".txt")
        assert len(filtered) == 1


class TestFilterByMinWaste:
    def test_basic(self):
        groups = [_group(0, 100, 2), _group(1, 100, 10)]
        filtered = filter_by_min_waste(groups, 500)
        assert len(filtered) == 1


class TestFilterByPattern:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="a",
                file_size=100,
                files=[_fi("/photo_001.jpg"), _fi("/photo_002.jpg")],
            ),
            DuplicateGroup(
                group_id=1,
                hash_value="b",
                file_size=100,
                files=[_fi("/doc.pdf"), _fi("/doc2.pdf")],
            ),
        ]
        filtered = filter_by_pattern(groups, "photo_*")
        assert len(filtered) == 1


class TestChainFilters:
    def test_basic(self):
        groups = [
            _group(0, 100, 2, ".txt"),
            _group(1, 1000, 5, ".txt"),
            _group(2, 500, 2, ".py"),
        ]
        filtered = chain_filters(
            groups,
            lambda g: filter_by_min_count(g, 2),
            lambda g: filter_by_extension(g, ".txt"),
        )
        assert len(filtered) == 2


class TestFormatFilterResult:
    def test_basic(self):
        text = format_filter_result(100, 25, "test")
        assert "25" in text
        assert "100" in text
