"""Tests for DupeClean group search module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_search import (
    GroupSearchResult,
    format_search_results,
    search_groups_by_extension,
    search_groups_by_filename,
    search_groups_by_path,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, ext: str = ".txt") -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=100,
        files=[_fi(f"/path/file{i}{ext}", 100, ext) for i in range(2)],
    )


class TestSearchGroupsByFilename:
    def test_match(self):
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
        result = search_groups_by_filename(groups, "photo_*")
        assert result.group_count == 1

    def test_no_match(self):
        groups = [_group(0)]
        result = search_groups_by_filename(groups, "nonexistent*")
        assert result.group_count == 0


class TestSearchGroupsByExtension:
    def test_match(self):
        groups = [_group(0, ".txt"), _group(1, ".py")]
        result = search_groups_by_extension(groups, ".txt")
        assert result.group_count == 1


class TestSearchGroupsByPath:
    def test_match(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="a",
                file_size=100,
                files=[_fi("/photos/a.jpg"), _fi("/photos/b.jpg")],
            ),
        ]
        result = search_groups_by_path(groups, "/photos/*")
        assert result.group_count == 1


class TestGroupSearchResult:
    def test_counts(self):
        result = GroupSearchResult()
        result.matching_groups.append(_group(0))
        result.matching_files.append((0, _fi("/a")))
        assert result.group_count == 1
        assert result.file_count == 1


class TestFormatSearchResults:
    def test_no_results(self):
        result = GroupSearchResult()
        assert "No matching" in format_search_results(result)

    def test_with_results(self):
        result = GroupSearchResult(
            matching_groups=[_group(0)],
            matching_files=[(0, _fi("/a"))],
        )
        text = format_search_results(result)
        assert "1 groups" in text
