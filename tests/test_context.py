"""Tests for DupeClean context module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.context import (
    CleanupContext,
    create_context,
    format_context,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCleanupContext:
    def test_total_groups(self):
        ctx = CleanupContext(
            root=Path("/test"),
            groups=[
                DuplicateGroup(
                    group_id=0, hash_value="a", file_size=100, files=[_fi("/a"), _fi("/b")]
                ),
                DuplicateGroup(
                    group_id=1, hash_value="b", file_size=200, files=[_fi("/c"), _fi("/d")]
                ),
            ],
        )
        assert ctx.total_groups == 2

    def test_total_duplicates(self):
        ctx = CleanupContext(
            root=Path("/test"),
            groups=[
                DuplicateGroup(
                    group_id=0,
                    hash_value="a",
                    file_size=100,
                    files=[_fi("/a"), _fi("/b"), _fi("/c")],
                ),
            ],
        )
        assert ctx.total_duplicates == 3

    def test_get_group(self):
        group = DuplicateGroup(group_id=5, hash_value="a", file_size=100, files=[_fi("/a")])
        ctx = CleanupContext(root=Path("/test"), groups=[group])
        assert ctx.get_group(5) is not None
        assert ctx.get_group(99) is None


class TestCreateContext:
    def test_basic(self):
        ctx = create_context(Path("/test"), [], [], "newest", False)
        assert ctx.strategy == "newest"
        assert ctx.dry_run is False


class TestFormatContext:
    def test_basic(self):
        ctx = CleanupContext(root=Path("/test"))
        text = format_context(ctx)
        assert "DRY RUN" in text
        assert "Cleanup Context" in text
