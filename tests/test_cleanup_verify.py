"""Tests for DupeClean cleanup verification module."""

from __future__ import annotations

from dupeclean.cleanup_verify import (
    CleanupVerification,
    VerificationCheck,
)


class TestCleanupVerification:
    def test_verify_file_deleted(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")
        f.unlink()

        verify = CleanupVerification()
        verify.verify_file_deleted(f)
        assert verify.passed == 1

    def test_verify_file_deleted_still_exists(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")

        verify = CleanupVerification()
        verify.verify_file_deleted(f)
        assert verify.failed == 1

    def test_verify_file_exists(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("hello")

        verify = CleanupVerification()
        verify.verify_file_exists(f)
        assert verify.passed == 1

    def test_verify_file_exists_missing(self, tmp_path):
        verify = CleanupVerification()
        verify.verify_file_exists(tmp_path / "nope")
        assert verify.failed == 1

    def test_verify_hardlink(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello")
        b.hardlink_to(a)

        verify = CleanupVerification()
        verify.verify_hardlink(a, b)
        assert verify.passed == 1

    def test_verify_not_hardlink(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("hello")
        b.write_text("hello")

        verify = CleanupVerification()
        verify.verify_hardlink(a, b)
        assert verify.failed == 1

    def test_is_clean(self):
        verify = CleanupVerification()
        verify.add(VerificationCheck(check_type="test", path="/a", passed=True))
        assert verify.is_clean is True

    def test_is_not_clean(self):
        verify = CleanupVerification()
        verify.add(VerificationCheck(check_type="test", path="/a", passed=False))
        assert verify.is_clean is False

    def test_render_clean(self):
        verify = CleanupVerification()
        verify.add(VerificationCheck(check_type="test", path="/a", passed=True))
        text = verify.render()
        assert "ALL OK" in text

    def test_render_with_failures(self):
        verify = CleanupVerification()
        verify.add(
            VerificationCheck(check_type="delete", path="/a", passed=False, message="Still exists")
        )
        text = verify.render()
        assert "ISSUES" in text
        assert "Still exists" in text


class TestVerificationCheck:
    def test_status_pass(self):
        check = VerificationCheck(check_type="test", path="/a", passed=True)
        assert check.status == "PASS"

    def test_status_fail(self):
        check = VerificationCheck(check_type="test", path="/a", passed=False)
        assert check.status == "FAIL"
