"""Tests for DupeClean summary module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.summary import (
    DedupSummary,
    create_summary,
    format_brief_summary,
    format_summary,
)


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _make_groups() -> list[DuplicateGroup]:
    return [
        DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=1000,
            files=[_fi("/a"), _fi("/b"), _fi("/c")],
        ),
        DuplicateGroup(
            group_id=1,
            hash_value="def",
            file_size=2000,
            files=[_fi("/d"), _fi("/e")],
        ),
    ]


class TestCreateSummary:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        groups = _make_groups()
        summary = create_summary(files, groups, 1.5)
        assert summary.total_files_scanned == 2
        assert summary.duplicate_groups == 2
        assert summary.scan_duration == 1.5

    def test_empty(self):
        summary = create_summary([], [], 0.0)
        assert summary.total_files_scanned == 0
        assert summary.duplicate_groups == 0

    def test_waste_percentage(self):
        files = [_fi("/a", 1000)]
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=500,
                files=[_fi("/a", 500), _fi("/b", 500)],
            ),
        ]
        summary = create_summary(files, groups)
        assert summary.waste_percentage > 0

    def test_most_common_ext(self):
        files = [_fi("/a.py", 100), _fi("/b.py", 100)]
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=files,
            ),
        ]
        summary = create_summary(files, groups)
        assert summary.most_common_ext == ".py"


class TestDedupSummary:
    def test_waste_percentage_zero(self):
        summary = DedupSummary()
        assert summary.waste_percentage == 0.0

    def test_dupe_percentage(self):
        summary = DedupSummary(total_files_scanned=100, duplicate_files=25)
        assert summary.dupe_percentage == 25.0


class TestFormatSummary:
    def test_basic(self):
        files = [_fi("/a", 100)]
        groups = _make_groups()
        summary = create_summary(files, groups)
        text = format_summary(summary)
        assert "Files scanned" in text
        assert "Duplicate groups" in text

    def test_with_largest_group(self):
        groups = _make_groups()
        summary = create_summary([], groups)
        text = format_summary(summary)
        assert "Largest" in text


class TestFormatBriefSummary:
    def test_no_duplicates(self):
        summary = DedupSummary()
        assert "No duplicates" in format_brief_summary(summary)

    def test_with_duplicates(self):
        summary = DedupSummary(
            duplicate_groups=5,
            duplicate_files=10,
            space_wasted=1024,
            total_size_scanned=10000,
        )
        text = format_brief_summary(summary)
        assert "5" in text
