"""Tests for DupeClean group hash module."""

from __future__ import annotations

from dupeclean.group_hash import (
    GroupHashResult,
    HashResult,
    find_hash_conflicts,
    format_hash_result,
    hash_group_files,
)
from dupeclean.models import FileInfo


class TestHashGroupFiles:
    def test_basic(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello")
        b.write_text("world")
        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        result = hash_group_files(files)
        assert result.count == 2

    def test_same_content(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        result = hash_group_files(files)
        assert result.results[0].hash_value == result.results[1].hash_value

    def test_sample_size(self, tmp_path):
        f = tmp_path / "big.bin"
        f.write_bytes(b"x" * 10000)
        files = [FileInfo.from_path(f)]
        files = [f for f in files if f is not None]
        result = hash_group_files(files, sample_size=100)
        assert result.count == 1


class TestFindHashConflicts:
    def test_conflicts(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        result = hash_group_files(files)
        conflicts = find_hash_conflicts(result)
        assert len(conflicts) == 1

    def test_no_conflicts(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("different")
        b.write_text("content")
        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        result = hash_group_files(files)
        conflicts = find_hash_conflicts(result)
        assert len(conflicts) == 0


class TestGroupHashResult:
    def test_get_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        files = [FileInfo.from_path(f)]
        files = [f for f in files if f is not None]
        result = hash_group_files(files)
        h = result.get_hash(str(f))
        assert h is not None


class TestFormatHashResult:
    def test_basic(self):
        result = GroupHashResult(
            results=[HashResult(path="/a", hash_value="abc", algorithm="sha256")]
        )
        text = format_hash_result(result)
        assert "1" in text
