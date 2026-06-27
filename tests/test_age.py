"""Tests for DupeClean age analysis module."""

from __future__ import annotations

import time

import pytest

from dupeclean.age import (
    analyze_file_ages,
    format_age,
    get_newest_files,
    get_oldest_files,
)
from dupeclean.models import FileInfo


@pytest.fixture
def files_with_ages(tmp_path) -> list[FileInfo]:
    """Create files with different modification times."""
    now = time.time()
    files = []
    test_cases = [
        ("today.txt", now - 3600),  # 1 hour ago
        ("week.txt", now - 86400 * 3),  # 3 days ago
        ("month.txt", now - 86400 * 15),  # 15 days ago
        ("year.txt", now - 86400 * 200),  # 200 days ago
        ("old.txt", now - 86400 * 500),  # 500 days ago
    ]
    for name, mtime in test_cases:
        p = tmp_path / name
        p.write_bytes(b"x" * 100)
        fi = FileInfo.from_path(p)
        if fi:
            fi.mtime = mtime
            files.append(fi)
    return files


class TestAnalyzeFileAges:
    def test_bucket_assignment(self, files_with_ages):
        buckets = analyze_file_ages(files_with_ages)
        assert len(buckets) > 0

        # Today bucket should have 1 file
        today = next(b for b in buckets if b.label == "Today")
        assert today.count == 1

        # This week bucket should have 1 file
        week = next(b for b in buckets if b.label == "This week")
        assert week.count == 1

    def test_total_files(self, files_with_ages):
        buckets = analyze_file_ages(files_with_ages)
        total = sum(b.count for b in buckets)
        assert total == len(files_with_ages)

    def test_empty_files(self):
        buckets = analyze_file_ages([])
        assert all(b.count == 0 for b in buckets)


class TestGetOldestFiles:
    def test_returns_sorted(self, files_with_ages):
        oldest = get_oldest_files(files_with_ages, 3)
        assert len(oldest) == 3
        assert oldest[0].path.name == "old.txt"

    def test_n_greater_than_files(self, files_with_ages):
        oldest = get_oldest_files(files_with_ages, 100)
        assert len(oldest) == len(files_with_ages)


class TestGetNewestFiles:
    def test_returns_sorted(self, files_with_ages):
        newest = get_newest_files(files_with_ages, 3)
        assert len(newest) == 3
        assert newest[0].path.name == "today.txt"


class TestFormatAge:
    def test_just_now(self):
        assert format_age(30) == "just now"

    def test_minutes(self):
        assert format_age(300) == "5m ago"

    def test_hours(self):
        assert format_age(7200) == "2h ago"

    def test_days(self):
        assert format_age(86400 * 5) == "5d ago"

    def test_months(self):
        assert format_age(86400 * 60) == "2mo ago"

    def test_years(self):
        assert format_age(86400 * 400) == "1y ago"
