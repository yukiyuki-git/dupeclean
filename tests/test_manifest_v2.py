"""Tests for DupeClean dedup manifest v2 module."""

from __future__ import annotations

import pytest

from dupeclean.manifest_v2 import (
    DedupManifest,
    ManifestEntry,
    format_manifest,
)


@pytest.fixture
def manifest():
    return DedupManifest(
        operation_id="test_op",
        timestamp=1000000,
        root="/test",
    )


class TestManifestEntry:
    def test_size_display(self):
        entry = ManifestEntry(path="/a", action="kept", size=1024)
        assert "B" in entry.size_display


class TestDedupManifest:
    def test_add_entry(self, manifest):
        manifest.add_entry(ManifestEntry(path="/a", action="kept"))
        assert manifest.total_entries == 1

    def test_kept_count(self, manifest):
        manifest.add_entry(ManifestEntry(path="/a", action="kept"))
        manifest.add_entry(ManifestEntry(path="/b", action="removed"))
        assert manifest.kept_count == 1

    def test_removed_count(self, manifest):
        manifest.add_entry(ManifestEntry(path="/a", action="kept"))
        manifest.add_entry(ManifestEntry(path="/b", action="removed"))
        manifest.add_entry(ManifestEntry(path="/c", action="hardlinked"))
        assert manifest.removed_count == 2

    def test_save_and_load(self, tmp_path, manifest):
        manifest.add_entry(ManifestEntry(path="/a", action="kept", size=100, hash_value="abc"))
        manifest.add_entry(ManifestEntry(path="/b", action="removed", size=100))

        path = tmp_path / "manifest.json"
        manifest.save(path)
        assert path.exists()

        loaded = DedupManifest.load(path)
        assert loaded is not None
        assert loaded.operation_id == "test_op"
        assert loaded.total_entries == 2

    def test_load_nonexistent(self, tmp_path):
        assert DedupManifest.load(tmp_path / "nope") is None


class TestFormatManifest:
    def test_basic(self, manifest):
        manifest.add_entry(ManifestEntry(path="/a", action="kept"))
        manifest.add_entry(ManifestEntry(path="/b", action="removed"))
        text = format_manifest(manifest)
        assert "test_op" in text
        assert "Kept" in text
        assert "Removed" in text

    def test_with_removed_files(self, manifest):
        manifest.add_entry(ManifestEntry(path="/test/file.txt", action="removed", size=1000))
        text = format_manifest(manifest)
        assert "file.txt" in text
