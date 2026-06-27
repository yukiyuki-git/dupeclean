"""Tests for DupeClean dedup engine v2."""

from __future__ import annotations

from dupeclean.dedup_v2 import (
    DedupV2Result,
    analyze_dedup_v2,
    fingerprint_file,
    format_dedup_v2,
)
from dupeclean.models import FileInfo


class TestFingerprintFile:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world " * 100)
        fp = fingerprint_file(f)
        assert fp is not None
        assert fp.size > 0
        assert fp.chunk_count > 0

    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"same content")
        fp1 = fingerprint_file(f)
        fp2 = fingerprint_file(f)
        assert fp1 is not None
        assert fp2 is not None
        assert fp1.full_hash == fp2.full_hash

    def test_different_content(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"content a")
        b.write_bytes(b"content b")
        fp_a = fingerprint_file(a)
        fp_b = fingerprint_file(b)
        assert fp_a is not None
        assert fp_b is not None
        assert fp_a.full_hash != fp_b.full_hash

    def test_nonexistent(self, tmp_path):
        assert fingerprint_file(tmp_path / "nope") is None

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        fp = fingerprint_file(f)
        assert fp is not None
        assert fp.chunk_count == 0


class TestAnalyzeDedupV2:
    def test_with_duplicates(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"same content " * 100)
        b.write_bytes(b"same content " * 100)

        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        result = analyze_dedup_v2(files)

        assert result.unique_files == 1
        assert result.duplicate_files == 1
        assert result.space_saved > 0

    def test_no_duplicates(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_bytes(b"unique a")
        b.write_bytes(b"unique b")

        files = [FileInfo.from_path(a), FileInfo.from_path(b)]
        files = [f for f in files if f is not None]
        result = analyze_dedup_v2(files)

        assert result.unique_files == 2
        assert result.duplicate_files == 0
        assert result.space_saved == 0

    def test_empty_list(self):
        result = analyze_dedup_v2([])
        assert result.unique_files == 0


class TestDedupV2Result:
    def test_dedup_ratio(self):
        result = DedupV2Result(unique_chunks=50, total_chunks=100)
        assert result.dedup_ratio == 0.5

    def test_zero_chunks(self):
        result = DedupV2Result()
        assert result.dedup_ratio == 0.0


class TestFormatDedupV2:
    def test_contains_stats(self):
        result = DedupV2Result(
            unique_files=10,
            duplicate_files=5,
            unique_chunks=100,
            total_chunks=150,
            space_saved=5000,
        )
        text = format_dedup_v2(result)
        assert "10" in text
        assert "5" in text
