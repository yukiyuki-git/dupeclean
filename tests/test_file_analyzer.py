"""Tests for DupeClean file analyzer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.file_analyzer import (
    FileAnalysis,
    analyze_file,
    analyze_files,
    format_file_analysis,
)
from dupeclean.models import FileInfo


class TestAnalyzeFile:
    def test_text_file(self, tmp_path):
        f = tmp_path / "text.txt"
        f.write_text("line 1\nline 2\nline 3")
        analysis = analyze_file(f)
        assert analysis is not None
        assert analysis.line_count == 3
        assert not analysis.is_binary

    def test_binary_file(self, tmp_path):
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01\x02\x03")
        analysis = analyze_file(f)
        assert analysis is not None
        assert analysis.is_binary

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        analysis = analyze_file(f)
        assert analysis is not None
        assert analysis.is_empty

    def test_hidden_file(self, tmp_path):
        f = tmp_path / ".hidden"
        f.write_text("secret")
        analysis = analyze_file(f)
        assert analysis is not None
        assert analysis.is_hidden

    def test_nonexistent(self, tmp_path):
        assert analyze_file(tmp_path / "nope") is None


class TestAnalyzeFiles:
    def test_multiple(self, tmp_path):
        for name in ["a.txt", "b.txt"]:
            (tmp_path / name).write_text("content")
        files = [FileInfo.from_path(tmp_path / name) for name in ["a.txt", "b.txt"]]
        files = [f for f in files if f is not None]
        results = analyze_files(files)
        assert len(results) == 2


class TestFormatFileAnalysis:
    def test_basic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        analysis = analyze_file(f)
        assert analysis is not None
        text = format_file_analysis(analysis)
        assert "test.txt" in text
        assert "5" in text  # size


class TestFileAnalysis:
    def test_size_display(self):
        analysis = FileAnalysis(path=Path("/test"), size=1024, extension=".txt")
        assert "B" in analysis.size_display
