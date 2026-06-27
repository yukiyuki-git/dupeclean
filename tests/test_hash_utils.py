"""Tests for DupeClean hashing utilities."""

from __future__ import annotations

from dupeclean.hash_utils import (
    HashResult,
    format_hash_result,
    hash_data,
    hash_file_full,
    hash_file_quick,
)


class TestHashFileQuick:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world " * 100)
        result = hash_file_quick(f)
        assert result is not None
        assert result.algorithm == "sha256_quick"
        assert len(result.hash_value) == 64

    def test_nonexistent(self, tmp_path):
        assert hash_file_quick(tmp_path / "nope") is None

    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("same content")
        r1 = hash_file_quick(f)
        r2 = hash_file_quick(f)
        assert r1 is not None and r2 is not None
        assert r1.hash_value == r2.hash_value


class TestHashFileFull:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        result = hash_file_full(f)
        assert result is not None
        assert result.algorithm == "sha256"
        assert result.file_size == 11

    def test_nonexistent(self, tmp_path):
        assert hash_file_full(tmp_path / "nope") is None

    def test_different_content(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("content a")
        b.write_text("content b")
        r_a = hash_file_full(a)
        r_b = hash_file_full(b)
        assert r_a is not None and r_b is not None
        assert r_a.hash_value != r_b.hash_value


class TestHashData:
    def test_basic(self):
        h = hash_data(b"hello")
        assert len(h) == 64

    def test_deterministic(self):
        assert hash_data(b"test") == hash_data(b"test")

    def test_different_data(self):
        assert hash_data(b"a") != hash_data(b"b")


class TestHashResult:
    def test_short_hash(self):
        result = HashResult(
            algorithm="sha256",
            hash_value="a" * 64,
            file_size=100,
        )
        assert result.short_hash == "a" * 16


class TestFormatHashResult:
    def test_basic(self):
        result = HashResult(
            algorithm="sha256",
            hash_value="abc123",
            file_size=1024,
        )
        text = format_hash_result(result)
        assert "sha256" in text
        assert "1,024" in text
