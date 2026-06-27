"""Tests for DupeClean checksum verification module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dupeclean.checksums import (
    ChecksumEntry,
    _guess_algorithm,
    format_manifest,
    generate_checksum,
    generate_manifest,
    parse_manifest,
    verify_manifest,
)


@pytest.fixture
def sample_files(tmp_path):
    files = []
    for name, content in [
        ("a.txt", b"hello world"),
        ("b.txt", b"goodbye world"),
        ("c.bin", b"\x00" * 1024),
    ]:
        p = tmp_path / name
        p.write_bytes(content)
        files.append(p)
    return files


class TestGenerateChecksum:
    def test_sha256(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = generate_checksum(f, "sha256")
        assert result is not None
        assert len(result) == 64  # sha256 hex length

    def test_md5(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = generate_checksum(f, "md5")
        assert result is not None
        assert len(result) == 32

    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        r1 = generate_checksum(f)
        r2 = generate_checksum(f)
        assert r1 == r2

    def test_different_content_different_hash(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello")
        b.write_text("world")
        assert generate_checksum(a) != generate_checksum(b)

    def test_nonexistent_file(self, tmp_path):
        result = generate_checksum(tmp_path / "nope")
        assert result is None


class TestGenerateManifest:
    def test_basic_manifest(self, sample_files):
        entries = generate_manifest(sample_files)
        assert len(entries) == len(sample_files)
        for entry in entries:
            assert len(entry.hash_value) == 64

    def test_with_root(self, sample_files, tmp_path):
        entries = generate_manifest(sample_files, root=tmp_path)
        assert len(entries) == len(sample_files)


class TestFormatManifest:
    def test_sha256sum_format(self, tmp_path):
        entries = [
            ChecksumEntry(
                hash_value="abc123",
                path=Path("/test/file.txt"),
                algorithm="sha256",
            ),
        ]
        text = format_manifest(entries)
        assert "abc123" in text
        assert "file.txt" in text

    def test_relative_paths(self, tmp_path):
        entries = [
            ChecksumEntry(
                hash_value="abc123",
                path=tmp_path / "file.txt",
                algorithm="sha256",
            ),
        ]
        text = format_manifest(entries, root=tmp_path, relative=True)
        assert "file.txt" in text


class TestParseManifest:
    def test_parse_basic(self):
        content = "abc123  file.txt\ndef456  other.txt"
        entries = parse_manifest(content)
        assert len(entries) == 2
        assert entries[0].hash_value == "abc123"
        assert entries[0].path == Path("file.txt")

    def test_skip_comments(self):
        content = "# Comment\nabc123  file.txt"
        entries = parse_manifest(content)
        assert len(entries) == 1

    def test_skip_empty_lines(self):
        content = "\nabc123  file.txt\n\n"
        entries = parse_manifest(content)
        assert len(entries) == 1

    def test_guess_algorithm(self):
        content = "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592  test.txt"
        entries = parse_manifest(content)
        assert entries[0].algorithm == "sha256"


class TestVerifyManifest:
    def test_valid_files(self, sample_files):
        entries = generate_manifest(sample_files)
        results = verify_manifest(entries)
        assert all(valid for _, valid in results)

    def test_corrupted_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("original")
        entries = generate_manifest([f])

        # Corrupt the file
        f.write_text("corrupted")
        results = verify_manifest(entries)
        assert not results[0][1]

    def test_nonexistent_file(self, tmp_path):
        entries = [
            ChecksumEntry(
                hash_value="abc123",
                path=tmp_path / "nope.txt",
                algorithm="sha256",
            ),
        ]
        results = verify_manifest(entries)
        assert not results[0][1]


class TestGuessAlgorithm:
    def test_md5(self):
        assert _guess_algorithm("a" * 32) == "md5"

    def test_sha1(self):
        assert _guess_algorithm("a" * 40) == "sha1"

    def test_sha256(self):
        assert _guess_algorithm("a" * 64) == "sha256"

    def test_sha512(self):
        assert _guess_algorithm("a" * 128) == "sha512"

    def test_unknown_defaults_to_sha256(self):
        assert _guess_algorithm("abc") == "sha256"
