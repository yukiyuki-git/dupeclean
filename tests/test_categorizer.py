"""Tests for DupeClean file categorizer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.categorizer import (
    CATEGORIES,
    Category,
    categorize_file,
    categorize_files,
    format_categories,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCategorizeFile:
    def test_code(self):
        assert categorize_file(_fi("/test.py")) == "code"
        assert categorize_file(_fi("/app.js")) == "code"

    def test_documents(self):
        assert categorize_file(_fi("/doc.pdf")) == "documents"
        assert categorize_file(_fi("/readme.txt")) == "documents"

    def test_images(self):
        assert categorize_file(_fi("/photo.jpg")) == "images"
        assert categorize_file(_fi("/icon.png")) == "images"

    def test_other(self):
        assert categorize_file(_fi("/unknown.xyz")) == "other"


class TestCategorizeFiles:
    def test_basic(self):
        files = [
            _fi("/code.py", 1000),
            _fi("/photo.jpg", 5000),
            _fi("/doc.pdf", 2000),
        ]
        cats = categorize_files(files)
        assert "code" in cats
        assert "images" in cats
        assert "documents" in cats

    def test_empty(self):
        cats = categorize_files([])
        assert len(cats) == 0


class TestCategory:
    def test_count(self):
        cat = Category(name="test", description="test", files=[_fi("/a"), _fi("/b")])
        assert cat.count == 2

    def test_total_size(self):
        cat = Category(name="test", description="test", files=[_fi("/a", 100), _fi("/b", 200)])
        assert cat.total_size == 300


class TestFormatCategories:
    def test_basic(self):
        cats = {
            "code": Category(name="Code", description="", files=[_fi("/a.py", 1000)]),
            "images": Category(name="Images", description="", files=[_fi("/b.jpg", 5000)]),
        }
        text = format_categories(cats)
        assert "Code" in text
        assert "Images" in text


class TestCategories:
    def test_all_exist(self):
        expected = {"documents", "images", "videos", "audio", "code", "archives", "data"}
        assert set(CATEGORIES.keys()) == expected
