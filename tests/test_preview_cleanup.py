"""Tests for DupeClean cleanup preview module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.preview_cleanup import (
    CleanupPreview,
    PreviewEntry,
    create_preview,
)


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCreatePreview:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=1000,
                files=[_fi("/a/file.txt"), _fi("/b/file.txt"), _fi("/c/file.txt")],
            )
        ]
        preview = create_preview(groups)
        assert preview.total_actions == 2

    def test_empty_groups(self):
        preview = create_preview([])
        assert preview.total_actions == 0

    def test_single_file_group_skipped(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a")],
            )
        ]
        preview = create_preview(groups)
        assert preview.total_actions == 0

    def test_total_savings(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a", 100), _fi("/b", 100)],
            )
        ]
        preview = create_preview(groups)
        assert preview.total_savings == 100


class TestCleanupPreview:
    def test_render_empty(self):
        preview = CleanupPreview()
        assert "No cleanup" in preview.render()

    def test_render_with_entries(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=500,
                files=[_fi("/a/data.bin"), _fi("/b/data.bin")],
            )
        ]
        preview = create_preview(groups)
        text = preview.render()
        assert "DEL" in text
        assert "data.bin" in text


class TestPreviewEntry:
    def test_size_display(self):
        entry = PreviewEntry(
            action="delete",
            file=_fi("/a", 1024),
        )
        assert "B" in entry.size_display
