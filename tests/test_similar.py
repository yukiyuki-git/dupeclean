"""Tests for DupeClean content similarity module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.similar import (
    SimilarityResult,
    byte_frequency_hash,
    chunk_hash,
    compare_byte_frequency,
    compare_chunks,
    find_similar_content,
    format_similarity_results,
)


class TestByteFrequencyHash:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world " * 100)
        result = byte_frequency_hash(f)
        assert result is not None
        assert len(result) == 256

    def test_nonexistent(self, tmp_path):
        assert byte_frequency_hash(tmp_path / "nope") is None

    def test_similar_content(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello world " * 100)
        b.write_text("hello world " * 100 + "extra")
        hash_a = byte_frequency_hash(a)
        hash_b = byte_frequency_hash(b)
        assert hash_a is not None
        assert hash_b is not None
        # Should be very similar
        assert hash_a == hash_b  # Same distribution for similar text


class TestChunkHash:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"x" * 100000)
        result = chunk_hash(f)
        assert result is not None
        assert len(result) == 8  # Default num_chunks

    def test_nonexistent(self, tmp_path):
        assert chunk_hash(tmp_path / "nope") is None

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        result = chunk_hash(f)
        assert result == []


class TestCompareByteFrequency:
    def test_identical_files(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("same content " * 100)
        b.write_text("same content " * 100)
        sim = compare_byte_frequency(a, b)
        assert sim > 0.95

    def test_different_files(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("a" * 1000)
        b.write_text("b" * 1000)
        sim = compare_byte_frequency(a, b)
        assert sim < 0.9

    def test_nonexistent(self, tmp_path):
        assert compare_byte_frequency(tmp_path / "a", tmp_path / "b") == 0.0


class TestCompareChunks:
    def test_identical_files(self, tmp_path):
        a = tmp_path / "a.bin"
        b = tmp_path / "b.bin"
        a.write_bytes(b"\x00" * 100000)
        b.write_bytes(b"\x00" * 100000)
        sim = compare_chunks(a, b)
        assert sim == 1.0

    def test_different_files(self, tmp_path):
        a = tmp_path / "a.bin"
        b = tmp_path / "b.bin"
        a.write_bytes(b"\x00" * 100000)
        b.write_bytes(b"\xff" * 100000)
        sim = compare_chunks(a, b)
        assert sim < 0.5

    def test_nonexistent(self, tmp_path):
        assert compare_chunks(tmp_path / "a", tmp_path / "b") == 0.0


class TestFindSimilarContent:
    def test_finds_similar(self, tmp_path):
        # Create files with similar content and similar sizes
        for name, content in [
            ("a.txt", b"hello " * 1000),
            ("b.txt", b"hello " * 999 + b"!"),
            ("c.txt", b"zzzzz " * 1000),
        ]:
            (tmp_path / name).write_bytes(content)
        files = [FileInfo.from_path(tmp_path / name) for name in ["a.txt", "b.txt", "c.txt"]]
        files = [f for f in files if f is not None]
        results = find_similar_content(files, threshold=0.5, method="byte_freq")
        assert len(results) >= 1

    def test_empty_list(self):
        assert find_similar_content([]) == []


class TestFormatSimilarityResults:
    def test_empty(self):
        assert "No similar" in format_similarity_results([])

    def test_with_results(self):
        results = [
            SimilarityResult(
                file_a=Path("/a.txt"),
                file_b=Path("/b.txt"),
                similarity=0.95,
                method="chunk",
            ),
        ]
        text = format_similarity_results(results)
        assert "95%" in text or "similar" in text
