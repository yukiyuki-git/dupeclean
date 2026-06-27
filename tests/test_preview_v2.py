"""Tests for DupeClean cleanup preview v2 module."""

from __future__ import annotations

from dupeclean.preview_v2 import (
    CleanupPreviewV2,
    PreviewItem,
    create_preview_v2,
)


class TestCleanupPreviewV2:
    def test_add(self):
        preview = CleanupPreviewV2()
        preview.add(PreviewItem(path="/a", action="delete"))
        assert preview.total_items == 1

    def test_total_savings(self):
        preview = CleanupPreviewV2()
        preview.add(PreviewItem(path="/a", action="delete", size=100))
        preview.add(PreviewItem(path="/b", action="delete", size=200))
        assert preview.total_savings == 300

    def test_render_empty(self):
        preview = CleanupPreviewV2()
        assert "No items" in preview.render()

    def test_render_with_items(self):
        preview = CleanupPreviewV2()
        preview.add(PreviewItem(path="/a.txt", action="delete", size=1000, reason="Duplicate"))
        text = preview.render()
        assert "a.txt" in text
        assert "delete" in text


class TestPreviewItem:
    def test_size_display(self):
        item = PreviewItem(path="/a", action="delete", size=1024)
        assert "B" in item.size_display


class TestCreatePreviewV2:
    def test_basic(self):
        preview = create_preview_v2([])
        assert preview.total_items == 0
