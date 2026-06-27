"""Tests for DupeClean dedup scanner module."""

from __future__ import annotations

from dupeclean.dedup_scanner import (
    format_scan_result,
    scan_for_duplicates,
)


class TestScanForDuplicates:
    def test_basic(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        result = scan_for_duplicates(tmp_path)
        assert result.file_count == 2
        assert result.total_size > 0

    def test_nested(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("b")
        result = scan_for_duplicates(tmp_path)
        assert result.file_count == 2

    def test_ignore_patterns(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "pkg.js").write_text("pkg")
        result = scan_for_duplicates(
            tmp_path, ignore_patterns=["node_modules"]
        )
        assert result.file_count == 1

    def test_empty_dir(self, tmp_path):
        result = scan_for_duplicates(tmp_path)
        assert result.file_count == 0

    def test_scan_time(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        result = scan_for_duplicates(tmp_path)
        assert result.scan_time >= 0


class TestScanResult:
    def test_total_size_display(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"x" * 1024)
        result = scan_for_duplicates(tmp_path)
        assert "B" in result.total_size_display


class TestFormatScanResult:
    def test_basic(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        result = scan_for_duplicates(tmp_path)
        text = format_scan_result(result)
        assert "Files" in text
        assert "Size" in text
