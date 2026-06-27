"""Tests for DupeClean integrity checker module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.integrity import (
    IntegrityResult,
    check_bit_rot,
    compute_hash,
    compute_multi_hash,
    format_integrity_result,
    verify_hash,
)


class TestComputeHash:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = compute_hash(f)
        assert result is not None
        assert result.is_valid is True
        assert len(result.hash_value) == 64  # sha256

    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        r1 = compute_hash(f)
        r2 = compute_hash(f)
        assert r1 is not None and r2 is not None
        assert r1.hash_value == r2.hash_value

    def test_algorithms(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        for algo in ["md5", "sha1", "sha256"]:
            result = compute_hash(f, algo)
            assert result is not None
            assert result.algorithm == algo

    def test_nonexistent(self, tmp_path):
        assert compute_hash(tmp_path / "nope") is None

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        result = compute_hash(f)
        assert result is not None
        assert result.file_size == 0


class TestVerifyHash:
    def test_matching(self, tmp_path):
        import hashlib

        f = tmp_path / "test.txt"
        f.write_text("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        result = verify_hash(f, expected)
        assert result is not None
        assert result.is_valid is True

    def test_non_matching(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = verify_hash(f, "wrong_hash")
        assert result is not None
        assert result.is_valid is False

    def test_nonexistent(self, tmp_path):
        assert verify_hash(tmp_path / "nope", "abc") is None


class TestComputeMultiHash:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        results = compute_multi_hash(f)
        assert "md5" in results
        assert "sha1" in results
        assert "sha256" in results

    def test_custom_algorithms(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        results = compute_multi_hash(f, ["sha256"])
        assert len(results) == 1
        assert "sha256" in results


class TestCheckBitRot:
    def test_no_rot(self, tmp_path):
        import hashlib

        f = tmp_path / "test.txt"
        f.write_text("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert check_bit_rot(f, expected) is True

    def test_with_rot(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("original")
        import hashlib

        original_hash = hashlib.sha256(b"original").hexdigest()
        f.write_text("corrupted")
        assert check_bit_rot(f, original_hash) is False


class TestFormatIntegrityResult:
    def test_valid(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = compute_hash(f)
        assert result is not None
        text = format_integrity_result(result)
        assert "OK" in text
        assert "test.txt" in text

    def test_invalid(self, tmp_path):
        result = IntegrityResult(
            path=Path("/test/bad.txt"),
            algorithm="sha256",
            hash_value="",
            file_size=100,
            is_valid=False,
            error="Read error",
        )
        text = format_integrity_result(result)
        assert "FAILED" in text
