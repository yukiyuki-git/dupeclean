"""Tests for DupeClean group scanner module."""

from __future__ import annotations

from dupeclean.group_scanner import (
    ScanConfig,
    format_scan_result,
    scan_directory,
)


class TestScanDirectory:
    def test_basic(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        result = scan_directory(tmp_path)
        assert result.file_count == 2

    def test_nested(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("b")
        result = scan_directory(tmp_path)
        assert result.file_count == 2

    def test_skip_hidden(self, tmp_path):
        (tmp_path / ".hidden").write_text("secret")
        (tmp_path / "visible.txt").write_text("visible")
        result = scan_directory(tmp_path)
        assert result.file_count == 1

    def test_empty_dir(self, tmp_path):
        result = scan_directory(tmp_path)
        assert result.file_count == 0

    def test_ignore_patterns(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        node = tmp_path / "node_modules"
        node.mkdir()
        (node / "pkg.js").write_text("pkg")
        config = ScanConfig(ignore_patterns=["node_modules"])
        result = scan_directory(tmp_path, config)
        assert result.file_count == 1


class TestScanResult:
    def test_total_size(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"x" * 1024)
        result = scan_directory(tmp_path)
        assert result.total_size == 1024


class TestFormatScanResult:
    def test_basic(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        result = scan_directory(tmp_path)
        text = format_scan_result(result)
        assert "1" in text
