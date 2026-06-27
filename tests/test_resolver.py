"""Tests for DupeClean resolver module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.resolver import (
    Resolution,
    ResolutionResult,
    format_resolution,
    resolve_group,
    resolve_groups,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestResolveGroup:
    def test_shortest_path(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[
                _fi("/very/long/path/file.txt"),
                _fi("/short/file.txt"),
            ],
        )
        resolution = resolve_group(group, "shortest")
        assert resolution.keeper.path.name == "file.txt"
        assert len(resolution.resolved) == 1

    def test_newest(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/a", mtime=100), _fi("/b", mtime=200)],
        )
        resolution = resolve_group(group, "newest")
        assert resolution.keeper.mtime == 200

    def test_oldest(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/a", mtime=100), _fi("/b", mtime=200)],
        )
        resolution = resolve_group(group, "oldest")
        assert resolution.keeper.mtime == 100

    def test_space_saved(self):
        group = DuplicateGroup(
            group_id=0,
            hash_value="abc",
            file_size=100,
            files=[_fi("/a", 100), _fi("/b", 100), _fi("/c", 100)],
        )
        resolution = resolve_group(group)
        assert resolution.space_saved == 200


class TestResolveGroups:
    def test_basic(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        result = resolve_groups(groups)
        assert result.total_resolved == 1

    def test_empty(self):
        result = resolve_groups([])
        assert result.total_resolved == 0


class TestResolutionResult:
    def test_total_saved(self):
        result = ResolutionResult(
            resolutions=[
                Resolution(group_id=0, strategy="test", keeper=_fi("/a"), space_saved=100),
                Resolution(group_id=1, strategy="test", keeper=_fi("/c"), space_saved=200),
            ]
        )
        assert result.total_saved == 300


class TestFormatResolution:
    def test_basic(self):
        result = ResolutionResult(
            resolutions=[
                Resolution(group_id=0, strategy="test", keeper=_fi("/a"), space_saved=100),
            ]
        )
        text = format_resolution(result)
        assert "1 groups" in text
