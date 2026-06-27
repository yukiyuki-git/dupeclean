"""Tests for DupeClean duplicate directory finder."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dupdirs import (
    DirFingerprint,
    DuplicateDirGroup,
    find_duplicate_directories,
    fingerprint_directory,
    format_duplicate_dirs,
)
from dupeclean.models import DirInfo, FileInfo


def _fi(path: str, size: int, hash_val: str = "") -> FileInfo:
    fi = FileInfo(path=Path(path), size=size, mtime=0)
    if hash_val:
        fi.quick_hash = hash_val
    return fi


class TestFingerprintDirectory:
    def test_basic_fingerprint(self):
        dir_info = DirInfo(path=Path("/test"), file_count=2, total_size=300)
        files = [
            _fi("/test/a.txt", 100, "hash_a"),
            _fi("/test/b.txt", 200, "hash_b"),
        ]
        fp = fingerprint_directory(dir_info, files)
        assert fp is not None
        assert fp.file_count == 2
        assert fp.total_size == 300

    def test_same_content_same_hash(self):
        dir1 = DirInfo(path=Path("/a"), file_count=2, total_size=300)
        dir2 = DirInfo(path=Path("/b"), file_count=2, total_size=300)
        files1 = [
            _fi("/a/x.txt", 100, "h1"),
            _fi("/a/y.txt", 200, "h2"),
        ]
        files2 = [
            _fi("/b/x.txt", 100, "h1"),
            _fi("/b/y.txt", 200, "h2"),
        ]

        fp1 = fingerprint_directory(dir1, files1)
        fp2 = fingerprint_directory(dir2, files2)
        assert fp1 is not None
        assert fp2 is not None
        assert fp1.content_hash == fp2.content_hash

    def test_different_content_different_hash(self):
        dir1 = DirInfo(path=Path("/a"), file_count=1, total_size=100)
        dir2 = DirInfo(path=Path("/b"), file_count=1, total_size=200)
        files1 = [_fi("/a/x.txt", 100, "h1")]
        files2 = [_fi("/b/x.txt", 200, "h2")]

        fp1 = fingerprint_directory(dir1, files1)
        fp2 = fingerprint_directory(dir2, files2)
        assert fp1 is not None
        assert fp2 is not None
        assert fp1.content_hash != fp2.content_hash

    def test_empty_directory(self):
        dir_info = DirInfo(path=Path("/empty"), file_count=0)
        fp = fingerprint_directory(dir_info, [])
        assert fp is None


class TestFindDuplicateDirectories:
    def test_finds_duplicates(self):
        dirs = {
            Path("/a"): DirInfo(path=Path("/a"), file_count=2, total_size=300),
            Path("/b"): DirInfo(path=Path("/b"), file_count=2, total_size=300),
        }
        files = [
            _fi("/a/x.txt", 100, "h1"),
            _fi("/a/y.txt", 200, "h2"),
            _fi("/b/x.txt", 100, "h1"),
            _fi("/b/y.txt", 200, "h2"),
        ]
        groups = find_duplicate_directories(dirs, files)
        assert len(groups) >= 1

    def test_no_duplicates(self):
        dirs = {
            Path("/a"): DirInfo(path=Path("/a"), file_count=1, total_size=100),
            Path("/b"): DirInfo(path=Path("/b"), file_count=1, total_size=200),
        }
        files = [
            _fi("/a/x.txt", 100, "h1"),
            _fi("/b/x.txt", 200, "h2"),
        ]
        groups = find_duplicate_directories(dirs, files)
        assert len(groups) == 0

    def test_empty_dirs(self):
        groups = find_duplicate_directories({}, [])
        assert len(groups) == 0


class TestDuplicateDirGroup:
    def test_wasted_space(self):
        fp = DirFingerprint(
            path=Path("/a"),
            file_count=2,
            total_size=1000,
            content_hash="abc",
        )
        group = DuplicateDirGroup(
            group_id=0,
            fingerprint=fp,
            directories=[fp, fp],
        )
        assert group.wasted_space == 1000  # 1000 * (2-1)


class TestFormatDuplicateDirs:
    def test_empty(self):
        assert "No duplicate" in format_duplicate_dirs([])

    def test_with_groups(self):
        fp = DirFingerprint(
            path=Path("/a"),
            file_count=2,
            total_size=1000,
            content_hash="abc",
        )
        groups = [DuplicateDirGroup(group_id=0, fingerprint=fp, directories=[fp, fp])]
        text = format_duplicate_dirs(groups)
        assert "Group #0" in text
