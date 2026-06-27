"""Tests for DupeClean file manifest module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dupeclean.manifest import (
    FileManifest,
    ManifestEntry,
    compare_manifests,
    format_manifest_summary,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestFileManifest:
    def test_from_files(self):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100), _fi("/test/b.txt", 200)]
        manifest = FileManifest.from_files(root, files)
        assert manifest.count == 2
        assert manifest.total_size == 300

    def test_to_json(self):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100)]
        manifest = FileManifest.from_files(root, files)
        json_str = manifest.to_json()
        data = json.loads(json_str)
        assert data["count"] == 1

    def test_to_csv(self):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100)]
        manifest = FileManifest.from_files(root, files)
        csv_str = manifest.to_csv()
        assert "path" in csv_str
        assert "a.txt" in csv_str

    def test_save_and_load_json(self, tmp_path):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100), _fi("/test/b.txt", 200)]
        manifest = FileManifest.from_files(root, files)

        save_path = tmp_path / "manifest.json"
        manifest.save(save_path, format="json")
        assert save_path.exists()

        loaded = FileManifest.load_json(save_path)
        assert loaded.count == 2
        assert loaded.total_size == 300

    def test_save_csv(self, tmp_path):
        root = Path("/test")
        files = [_fi("/test/a.txt", 100)]
        manifest = FileManifest.from_files(root, files)

        save_path = tmp_path / "manifest.csv"
        manifest.save(save_path, format="csv")
        assert save_path.exists()

    def test_invalid_format(self, tmp_path):
        manifest = FileManifest(root=Path("/test"))
        with pytest.raises(ValueError):
            manifest.save(tmp_path / "test.xml", format="xml")


class TestManifestEntry:
    def test_size_display(self):
        entry = ManifestEntry(path="test.txt", size=1024, mtime=0, extension=".txt")
        assert "B" in entry.size_display


class TestCompareManifests:
    def test_no_changes(self):
        files = [_fi("/test/a.txt", 100)]
        old = FileManifest.from_files(Path("/test"), files)
        new = FileManifest.from_files(Path("/test"), files)
        diff = compare_manifests(old, new)
        assert len(diff["added"]) == 0
        assert len(diff["removed"]) == 0
        assert diff["unchanged"] == 1

    def test_added_files(self):
        old_files = [_fi("/test/a.txt", 100)]
        new_files = [_fi("/test/a.txt", 100), _fi("/test/b.txt", 200)]
        old = FileManifest.from_files(Path("/test"), old_files)
        new = FileManifest.from_files(Path("/test"), new_files)
        diff = compare_manifests(old, new)
        assert len(diff["added"]) == 1
        assert diff["added"][0].path == "b.txt"

    def test_removed_files(self):
        old_files = [_fi("/test/a.txt", 100), _fi("/test/b.txt", 200)]
        new_files = [_fi("/test/a.txt", 100)]
        old = FileManifest.from_files(Path("/test"), old_files)
        new = FileManifest.from_files(Path("/test"), new_files)
        diff = compare_manifests(old, new)
        assert len(diff["removed"]) == 1

    def test_modified_files(self):
        old_files = [_fi("/test/a.txt", 100, 1.0)]
        new_files = [_fi("/test/a.txt", 200, 2.0)]
        old = FileManifest.from_files(Path("/test"), old_files)
        new = FileManifest.from_files(Path("/test"), new_files)
        diff = compare_manifests(old, new)
        assert len(diff["modified"]) == 1


class TestFormatManifestSummary:
    def test_contains_stats(self):
        files = [_fi("/test/a.txt", 100), _fi("/test/b.py", 200)]
        manifest = FileManifest.from_files(Path("/test"), files)
        text = format_manifest_summary(manifest)
        assert "Files:" in text
        assert "Total:" in text
        assert "Top types:" in text
