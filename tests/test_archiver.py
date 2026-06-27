"""Tests for DupeClean file archiver module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.archiver import (
    ArchiveResult,
    archive_files,
    format_archive_result,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestArchiveFiles:
    def test_dry_run(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            f = tmp_path / name
            f.write_text("content")
            fi = FileInfo.from_path(f)
            if fi:
                files.append(fi)

        archive_path = tmp_path / "archive.tar.gz"
        result = archive_files(files, archive_path, dry_run=True)
        assert result.succeeded == 2
        assert result.original_size > 0

    def test_actual_archive(self, tmp_path):
        files = []
        for name in ["a.txt", "b.txt"]:
            f = tmp_path / name
            f.write_text("content " * 100)
            fi = FileInfo.from_path(f)
            if fi:
                files.append(fi)

        archive_path = tmp_path / "archive.tar.gz"
        result = archive_files(files, archive_path, dry_run=False)
        assert result.succeeded == 2
        assert archive_path.exists()
        assert result.archive_size > 0


class TestArchiveResult:
    def test_compression_ratio(self):
        result = ArchiveResult(original_size=1000, archive_size=500)
        assert result.compression_ratio == 0.5

    def test_zero_original(self):
        result = ArchiveResult()
        assert result.compression_ratio == 0.0


class TestFormatArchiveResult:
    def test_basic(self, tmp_path):
        files = []
        f = tmp_path / "test.txt"
        f.write_text("content")
        fi = FileInfo.from_path(f)
        if fi:
            files.append(fi)

        archive_path = tmp_path / "test.tar.gz"
        result = archive_files(files, archive_path, dry_run=True)
        text = format_archive_result(result)
        assert "2" in text or "1" in text
