"""Tests for DupeClean fuzzy filename matcher."""

from __future__ import annotations

from pathlib import Path

from dupeclean.fuzzy import (
    extract_version,
    find_copy_pairs,
    find_similar_names,
    normalize_filename,
    similarity_score,
)
from dupeclean.models import FileInfo


def _make_file(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestNormalizeFilename:
    def test_basic(self):
        assert normalize_filename("photo.jpg") == "photo"

    def test_copy_suffix(self):
        result = normalize_filename("photo (1).jpg")
        assert "photo" in result
        assert "1" not in result or result == "photo"

    def test_dash_copy(self):
        result = normalize_filename("report - Copy.pdf")
        assert "report" in result.lower()

    def test_version_number(self):
        result = normalize_filename("document_v2.txt")
        assert "document" in result.lower()

    def test_case_insensitive(self):
        result = normalize_filename("README.md")
        assert result == "readme"

    def test_underscores(self):
        result = normalize_filename("my_file_name.txt")
        assert "my" in result
        assert "file" in result


class TestSimilarityScore:
    def test_identical(self):
        assert similarity_score("photo.jpg", "photo.jpg") == 1.0

    def test_copy(self):
        score = similarity_score("photo.jpg", "photo (1).jpg")
        assert score > 0.7

    def test_different(self):
        score = similarity_score("cat.jpg", "dog.jpg")
        assert score < 0.5

    def test_version_variants(self):
        score = similarity_score("report_v1.pdf", "report_v2.pdf")
        assert score > 0.8


class TestExtractVersion:
    def test_simple_version(self):
        assert extract_version("file_v2.txt") == "2"

    def test_semver(self):
        assert extract_version("app-1.2.3.zip") == "1.2.3"

    def test_no_version(self):
        assert extract_version("photo.jpg") is None


class TestFindSimilarNames:
    def test_finds_similar_group(self):
        files = [
            _make_file("/photos/IMG_001.jpg"),
            _make_file("/photos/IMG_002.jpg"),
            _make_file("/photos/IMG_003.jpg"),
            _make_file("/photos/other.txt"),
        ]
        groups = find_similar_names(files, threshold=0.6)
        assert len(groups) >= 1
        assert any(g.count >= 2 for g in groups)

    def test_different_extensions_not_grouped(self):
        files = [
            _make_file("/test/photo.jpg"),
            _make_file("/test/photo.png"),
        ]
        groups = find_similar_names(files, threshold=0.5)
        assert len(groups) == 0

    def test_same_extension_grouped(self):
        files = [
            _make_file("/test/report_v1.pdf"),
            _make_file("/test/report_v2.pdf"),
            _make_file("/test/report_v3.pdf"),
        ]
        groups = find_similar_names(files, threshold=0.6)
        assert len(groups) >= 1

    def test_empty_list(self):
        assert find_similar_names([]) == []

    def test_single_file(self):
        assert find_similar_names([_make_file("/a.txt")]) == []

    def test_groups_sorted_by_count(self):
        files = [
            _make_file("/a/photo_1.jpg"),
            _make_file("/a/photo_2.jpg"),
            _make_file("/a/photo_3.jpg"),
            _make_file("/b/doc_a.pdf"),
            _make_file("/b/doc_b.pdf"),
        ]
        groups = find_similar_names(files, threshold=0.5)
        if len(groups) >= 2:
            assert groups[0].count >= groups[1].count


class TestFindCopyPairs:
    def test_basic_copy(self):
        files = [
            _make_file("/test/photo.jpg"),
            _make_file("/test/photo (1).jpg"),
        ]
        pairs = find_copy_pairs(files)
        assert len(pairs) == 1
        assert pairs[0][0].path.name == "photo.jpg"
        assert pairs[0][1].path.name == "photo (1).jpg"

    def test_multiple_copies(self):
        files = [
            _make_file("/test/doc.pdf"),
            _make_file("/test/doc (1).pdf"),
            _make_file("/test/doc (2).pdf"),
        ]
        pairs = find_copy_pairs(files)
        assert len(pairs) == 2

    def test_no_copies(self):
        files = [
            _make_file("/test/a.txt"),
            _make_file("/test/b.txt"),
        ]
        pairs = find_copy_pairs(files)
        assert len(pairs) == 0
