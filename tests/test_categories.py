"""Tests for DupeClean file categorization module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.categories import (
    CATEGORIES,
    CategoryInfo,
    categorize_file,
    categorize_files,
    format_categories,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestCategorizeFile:
    def test_code(self):
        assert categorize_file(_fi("/test.py")) == "code"
        assert categorize_file(_fi("/app.js")) == "code"
        assert categorize_file(_fi("/main.go")) == "code"

    def test_documents(self):
        assert categorize_file(_fi("/doc.pdf")) == "documents"
        assert categorize_file(_fi("/readme.docx")) == "documents"

    def test_images(self):
        assert categorize_file(_fi("/photo.jpg")) == "images"
        assert categorize_file(_fi("/icon.png")) == "images"

    def test_video(self):
        assert categorize_file(_fi("/movie.mp4")) == "video"

    def test_audio(self):
        assert categorize_file(_fi("/song.mp3")) == "audio"

    def test_archives(self):
        assert categorize_file(_fi("/data.zip")) == "archives"

    def test_markup(self):
        assert categorize_file(_fi("/index.html")) == "markup"
        assert categorize_file(_fi("/config.yaml")) == "markup"

    def test_other(self):
        assert categorize_file(_fi("/unknown.xyz")) == "other"

    def test_case_insensitive(self):
        assert categorize_file(_fi("/FILE.PY")) == "code"
        assert categorize_file(_fi("/FILE.JPG")) == "images"


class TestCategorizeFiles:
    def test_basic(self):
        files = [
            _fi("/code.py", 1000),
            _fi("/photo.jpg", 5000),
            _fi("/doc.pdf", 2000),
            _fi("/script.js", 800),
        ]
        cats = categorize_files(files)
        assert "code" in cats
        assert "images" in cats
        assert "documents" in cats
        assert cats["images"].total_size == 5000

    def test_empty(self):
        cats = categorize_files([])
        assert len(cats) == 0

    def test_multiple_same_category(self):
        files = [_fi("/a.py"), _fi("/b.py"), _fi("/c.js")]
        cats = categorize_files(files)
        assert cats["code"].count == 3


class TestCategoryInfo:
    def test_count(self):
        info = CategoryInfo(name="test", files=[_fi("/a"), _fi("/b")])
        assert info.count == 2

    def test_total_size(self):
        info = CategoryInfo(name="test", files=[_fi("/a", 100), _fi("/b", 200)])
        assert info.total_size == 300


class TestFormatCategories:
    def test_empty(self):
        assert "No files" in format_categories({})

    def test_with_categories(self):
        files = [_fi("/a.py", 1000), _fi("/b.jpg", 5000)]
        cats = categorize_files(files)
        text = format_categories(cats)
        assert "code" in text
        assert "images" in text


class TestCategories:
    def test_all_categories_exist(self):
        expected = {
            "documents",
            "spreadsheets",
            "presentations",
            "images",
            "video",
            "audio",
            "archives",
            "code",
            "markup",
            "data",
            "executables",
            "fonts",
        }
        assert set(CATEGORIES.keys()) == expected
