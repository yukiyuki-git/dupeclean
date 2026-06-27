"""Tests for DupeClean file preview module."""

from __future__ import annotations

from dupeclean.models import FileInfo
from dupeclean.preview import (
    _is_likely_binary,
    format_preview,
    preview_file,
    preview_files,
)


class TestPreviewFile:
    def test_text_file(self, tmp_path):
        f = tmp_path / "text.txt"
        f.write_text("line 1\nline 2\nline 3")
        preview = preview_file(f)
        assert preview is not None
        assert "line 1" in preview.preview
        assert not preview.is_binary

    def test_binary_file(self, tmp_path):
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01\x02\x03")
        preview = preview_file(f)
        assert preview is not None
        assert preview.is_binary
        assert "Binary" in preview.preview

    def test_nonexistent(self, tmp_path):
        assert preview_file(tmp_path / "nope") is None

    def test_max_lines(self, tmp_path):
        f = tmp_path / "long.txt"
        f.write_text("\n".join(f"line {i}" for i in range(100)))
        preview = preview_file(f, max_lines=5)
        assert preview is not None
        assert preview.truncated is True

    def test_max_chars(self, tmp_path):
        f = tmp_path / "big.txt"
        f.write_text("x" * 5000)
        preview = preview_file(f, max_chars=100)
        assert preview is not None
        assert len(preview.preview) <= 100

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        preview = preview_file(f)
        assert preview is not None
        assert preview.preview == ""


class TestIsLikelyBinary:
    def test_text(self, tmp_path):
        f = tmp_path / "text.txt"
        f.write_text("hello")
        assert _is_likely_binary(f) is False

    def test_binary(self, tmp_path):
        f = tmp_path / "bin.dat"
        f.write_bytes(b"\x00\x01\x02")
        assert _is_likely_binary(f) is True

    def test_nonexistent(self, tmp_path):
        assert _is_likely_binary(tmp_path / "nope") is False


class TestFormatPreview:
    def test_contains_path(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        preview = preview_file(f)
        assert preview is not None
        text = format_preview(preview)
        assert "test.txt" in text

    def test_contains_size(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        preview = preview_file(f)
        assert preview is not None
        text = format_preview(preview)
        assert "B" in text

    def test_truncated_marker(self, tmp_path):
        f = tmp_path / "long.txt"
        f.write_text("\n".join(f"line {i}" for i in range(100)))
        preview = preview_file(f, max_lines=5)
        assert preview is not None
        text = format_preview(preview)
        if preview.truncated:
            assert "truncated" in text


class TestPreviewFiles:
    def test_multiple_files(self, tmp_path):
        for name in ["a.txt", "b.txt", "c.txt"]:
            (tmp_path / name).write_text(f"content of {name}")
        files = [
            FileInfo.from_path(tmp_path / name)
            for name in ["a.txt", "b.txt", "c.txt"]
        ]
        files = [f for f in files if f is not None]
        previews = preview_files(files)
        assert len(previews) == 3

    def test_max_files(self, tmp_path):
        for i in range(10):
            (tmp_path / f"f{i}.txt").write_text(f"content {i}")
        files = [
            FileInfo.from_path(tmp_path / f"f{i}.txt")
            for i in range(10)
        ]
        files = [f for f in files if f is not None]
        previews = preview_files(files, max_files=3)
        assert len(previews) == 3
