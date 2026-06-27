"""Tests for DupeClean enhanced scanner v2 module."""

from __future__ import annotations

from dupeclean.scanner_v2 import (
    format_scan_result_v2,
    scan_directory_v2,
)


class TestScanDirectoryV2:
    def test_basic(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        result = scan_directory_v2(tmp_path)
        assert result.file_count == 2

    def test_nested(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("b")
        result = scan_directory_v2(tmp_path)
        assert result.file_count == 2

    def test_ignore_hidden(self, tmp_path):
        (tmp_path / ".hidden").write_text("secret")
        (tmp_path / "visible.txt").write_text("visible")
        result = scan_directory_v2(tmp_path)
        assert result.file_count == 1

    def test_empty_dir(self, tmp_path):
        result = scan_directory_v2(tmp_path)
        assert result.file_count == 0

    def test_scan_time(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        result = scan_directory_v2(tmp_path)
        assert result.scan_time >= 0


class TestScanResultV2:
    def test_total_size(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"x" * 1024)
        result = scan_directory_v2(tmp_path)
        assert result.total_size == 1024

    def test_total_size_display(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"x" * 2048)
        result = scan_directory_v2(tmp_path)
        assert "B" in result.total_size_display


class TestFormatScanResultV2:
    def test_basic(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        result = scan_directory_v2(tmp_path)
        text = format_scan_result_v2(result)
        assert "Files" in text
        assert "Size" in text
