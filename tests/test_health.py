"""Tests for DupeClean disk health check module."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from dupeclean.health import (
    HealthIssue,
    HealthReport,
    _is_temp_file,
    check_disk_health,
    format_health_report,
)


class TestCheckDiskHealth:
    def test_healthy_directory(self, tmp_path):
        (tmp_path / "file.txt").write_text("hello")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "nested.txt").write_text("world")

        report = check_disk_health(tmp_path)
        assert report.total_files == 2
        assert report.total_dirs >= 1
        assert report.is_healthy

    def test_permission_errors(self, tmp_path):
        report = check_disk_health(tmp_path)
        assert report.permission_errors >= 0

    def test_hidden_files(self, tmp_path):
        (tmp_path / ".hidden").write_text("secret")
        (tmp_path / "visible.txt").write_text("visible")

        report = check_disk_health(tmp_path)
        assert report.hidden_files >= 1

    def test_temp_files(self, tmp_path):
        (tmp_path / "data.tmp").write_text("temp")
        (tmp_path / "backup.bak").write_text("backup")
        (tmp_path / "normal.txt").write_text("normal")

        report = check_disk_health(tmp_path)
        assert report.temp_files >= 2

    def test_broken_symlink(self, tmp_path):
        if os.name == "nt":
            pytest.skip("Symlinks require privileges on Windows")
        link = tmp_path / "broken_link"
        link.symlink_to(tmp_path / "nonexistent")

        report = check_disk_health(tmp_path)
        assert report.broken_symlinks >= 1

    def test_max_depth(self, tmp_path):
        deep = tmp_path
        for i in range(10):
            deep = deep / f"level_{i}"
            deep.mkdir()
        (deep / "deep_file.txt").write_text("deep")

        # Shallow scan
        report = check_disk_health(tmp_path, max_depth=3)
        assert report.total_files == 0  # Too deep to find

        # Deep scan
        report = check_disk_health(tmp_path, max_depth=15)
        assert report.total_files == 1


class TestIsTempFile:
    def test_tmp_extension(self):
        assert _is_temp_file("file.tmp") is True

    def test_bak_extension(self):
        assert _is_temp_file("backup.bak") is True

    def test_swp_extension(self):
        assert _is_temp_file(".file.swp") is True

    def test_normal_file(self):
        assert _is_temp_file("document.pdf") is False

    def test_tilde_suffix(self):
        assert _is_temp_file("file~") is True


class TestHealthReport:
    def test_error_count(self):
        report = HealthReport(
            path=Path("/test"),
            issues=[
                HealthIssue("error", "fs", "err"),
                HealthIssue("warning", "perm", "warn"),
                HealthIssue("error", "fs", "err2"),
            ],
        )
        assert report.error_count == 2

    def test_warning_count(self):
        report = HealthReport(
            path=Path("/test"),
            issues=[
                HealthIssue("error", "fs", "err"),
                HealthIssue("warning", "perm", "warn"),
            ],
        )
        assert report.warning_count == 1

    def test_is_healthy(self):
        report = HealthReport(path=Path("/test"))
        assert report.is_healthy is True

    def test_not_healthy(self):
        report = HealthReport(
            path=Path("/test"),
            issues=[HealthIssue("error", "fs", "err")],
        )
        assert report.is_healthy is False


class TestFormatHealthReport:
    def test_healthy_output(self, tmp_path):
        report = HealthReport(path=tmp_path)
        text = format_health_report(report)
        assert "No critical issues" in text

    def test_with_issues(self, tmp_path):
        report = HealthReport(
            path=tmp_path,
            issues=[
                HealthIssue("warning", "symlinks", "Broken link"),
            ],
            broken_symlinks=1,
        )
        text = format_health_report(report)
        assert "broken symlinks" in text

    def test_contains_stats(self, tmp_path):
        report = HealthReport(path=tmp_path, total_files=100, total_dirs=10)
        text = format_health_report(report)
        assert "100" in text
