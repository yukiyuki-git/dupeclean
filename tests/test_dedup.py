"""Tests for DupeClean duplicate finder."""
from pathlib import Path
import pytest
from dupeclean.config import Config
from dupeclean.dedup import DuplicateFinder, quick_find_duplicates, update_scan_stats
from dupeclean.models import FileInfo, ScanStats


@pytest.fixture
def dupe_files(tmp_path):
    files = []
    for name in ("dup_a1.txt", "dup_a2.txt", "dup_a3.txt"):
        p = tmp_path / name
        p.write_bytes(b"identical content here " * 100)
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)
    for name in ("dup_b1.dat", "dup_b2.dat"):
        p = tmp_path / name
        p.write_bytes(b"other content " * 200)
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)
    for name, content in [("unique1.txt", b"unique 1"), ("unique2.txt", b"unique 2"), ("unique3.txt", b"unique 3")]:
        p = tmp_path / name
        p.write_bytes(content)
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)
    return files


class TestDuplicateFinder:
    def test_find_duplicates(self, dupe_files):
        finder = DuplicateFinder()
        groups = finder.find_duplicates(dupe_files)
        assert len(groups) == 2
        g1 = groups[0] if groups[0].count == 3 else groups[1]
        assert g1.count == 3

    def test_no_duplicates(self, tmp_path):
        files = []
        for i in range(5):
            p = tmp_path / f"unique_{i}.txt"
            p.write_bytes(f"unique content {i}".encode())
            fi = FileInfo.from_path(p)
            if fi:
                files.append(fi)
        finder = DuplicateFinder()
        groups = finder.find_duplicates(files)
        assert len(groups) == 0

    def test_quick_find(self, dupe_files):
        groups = quick_find_duplicates(dupe_files)
        assert len(groups) == 2

    def test_update_scan_stats(self, dupe_files):
        finder = DuplicateFinder()
        groups = finder.find_duplicates(dupe_files)
        stats = ScanStats(total_files=len(dupe_files))
        update_scan_stats(stats, groups)
        assert stats.duplicate_groups == 2
        assert stats.duplicate_files == 5
        assert stats.wasted_space > 0

    def test_empty_files_not_grouped(self, tmp_path):
        files = []
        for i in range(3):
            p = tmp_path / f"empty_{i}.txt"
            p.write_bytes(b"")
            fi = FileInfo.from_path(p)
            if fi:
                files.append(fi)
        finder = DuplicateFinder()
        groups = finder.find_duplicates(files)
        assert len(groups) == 0
