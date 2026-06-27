"""Tests for DupeClean verification module."""

from __future__ import annotations

import hashlib

from dupeclean.verify import (
    VerificationReport,
    VerificationResult,
    format_verification_report,
    verify_file,
    verify_files,
)


class TestVerifyFile:
    def test_valid(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        result = verify_file(f, expected)
        assert result.is_valid is True

    def test_invalid(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = verify_file(f, "wrong_hash")
        assert result.is_valid is False

    def test_nonexistent(self, tmp_path):
        result = verify_file(tmp_path / "nope", "abc")
        assert result.is_valid is False
        assert result.error != ""


class TestVerifyFiles:
    def test_all_valid(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello")
        f2.write_text("world")
        h1 = hashlib.sha256(b"hello").hexdigest()
        h2 = hashlib.sha256(b"world").hexdigest()

        files = {f1: h1, f2: h2}
        report = verify_files(files)
        assert report.is_clean is True
        assert report.total_valid == 2

    def test_with_invalid(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        files = {f: "wrong_hash"}
        report = verify_files(files)
        assert report.total_invalid == 1


class TestVerificationReport:
    def test_is_clean(self):
        report = VerificationReport(
            total_checked=10,
            total_valid=10,
            total_invalid=0,
            total_errors=0,
        )
        assert report.is_clean is True

    def test_success_rate(self):
        report = VerificationReport(total_checked=10, total_valid=8)
        assert report.success_rate == 0.8


class TestFormatVerificationReport:
    def test_clean(self):
        report = VerificationReport(total_checked=10, total_valid=10)
        text = format_verification_report(report)
        assert "OK" in text

    def test_with_errors(self, tmp_path):
        report = VerificationReport(
            total_checked=2,
            total_valid=1,
            total_invalid=1,
            results=[
                VerificationResult(
                    path=tmp_path / "bad.txt",
                    expected_hash="abc",
                    actual_hash="def",
                    is_valid=False,
                ),
            ],
        )
        text = format_verification_report(report)
        assert "Invalid" in text or "invalid" in text
