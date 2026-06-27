"""Tests for DupeClean file preview module."""

from __future__ import annotations

from dupeclean.file_preview import (
    format_preview_data,
    preview_file_content,
    preview_multiple,
)
from dupeclean.models import FileInfo


class TestPreviewFileContent:
    def test_text_file(self, tmp_path):
        f = tmp_path / "text.txt"
        f.write_text("line 1\nline 2\nline 3")
        preview = preview_file_content(f)
        assert preview is not None
        assert "line 1" in preview.preview
        assert not preview.is_binary

    def test_binary_file(self, tmp_path):
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01\x02\x03")
        preview = preview_file_content(f)
        assert preview is not None
        assert preview.is_binary

    def test_nonexistent(self, tmp_path):
        assert preview_file_content(tmp_path / "nope") is None

    def test_max_lines(self, tmp_path):
        f = tmp_path / "long.txt"
        f.write_text("\n".join(f"line {i}" for i in range(100)))
        preview = preview_file_content(f, max_lines=5)
        assert preview is not None
        assert preview.truncated is True

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        preview = preview_file_content(f)
        assert preview is not None


class TestFormatPreviewData:
    def test_contains_path(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        preview = preview_file_content(f)
        assert preview is not None
        text = format_preview_data(preview)
        assert "test.txt" in text


class TestPreviewMultiple:
    def test_multiple_files(self, tmp_path):
        for name in ["a.txt", "b.txt", "c.txt"]:
            (tmp_path / name).write_text(f"content of {name}")
        files = [FileInfo.from_path(tmp_path / name) for name in ["a.txt", "b.txt", "c.txt"]]
        files = [f for f in files if f is not None]
        previews = preview_multiple(files)
        assert len(previews) == 3

    def test_max_files(self, tmp_path):
        for i in range(10):
            (tmp_path / f"f{i}.txt").write_text(f"content {i}")
        files = [FileInfo.from_path(tmp_path / f"f{i}.txt") for i in range(10)]
        files = [f for f in files if f is not None]
        previews = preview_multiple(files, max_files=3)
        assert len(previews) == 3
