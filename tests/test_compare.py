"""Tests for DupeClean directory comparison module."""

from __future__ import annotations

import pytest

from dupeclean.compare import CompareResult, compare_directories


@pytest.fixture
def two_dirs(tmp_path):
    """Create two directory trees for comparison."""
    dir_a = tmp_path / "dir_a"
    dir_b = tmp_path / "dir_b"
    dir_a.mkdir()
    dir_b.mkdir()

    # Files only in A
    (dir_a / "only_a.txt").write_text("only in a")

    # Files only in B
    (dir_b / "only_b.txt").write_text("only in b")

    # Files in both, identical content
    (dir_a / "shared.txt").write_bytes(b"shared content")
    (dir_b / "shared.txt").write_bytes(b"shared content")

    # Files in both, different content
    (dir_a / "modified.txt").write_text("version A")
    (dir_b / "modified.txt").write_text("version B")

    # Subdirectories
    sub_a = dir_a / "sub"
    sub_b = dir_b / "sub"
    sub_a.mkdir()
    sub_b.mkdir()
    (sub_a / "deep.txt").write_text("deep a")
    (sub_b / "deep.txt").write_text("deep a")  # Same

    return dir_a, dir_b


class TestCompareDirectories:
    def test_basic_comparison(self, two_dirs):
        dir_a, dir_b = two_dirs
        result = compare_directories(dir_a, dir_b)

        assert isinstance(result, CompareResult)
        assert result.path_a == dir_a
        assert result.path_b == dir_b

    def test_only_in_a(self, two_dirs):
        dir_a, dir_b = two_dirs
        result = compare_directories(dir_a, dir_b)

        names_a = {f.path.name for f in result.only_in_a}
        assert "only_a.txt" in names_a

    def test_only_in_b(self, two_dirs):
        dir_a, dir_b = two_dirs
        result = compare_directories(dir_a, dir_b)

        names_b = {f.path.name for f in result.only_in_b}
        assert "only_b.txt" in names_b

    def test_identical_files(self, two_dirs):
        dir_a, dir_b = two_dirs
        result = compare_directories(dir_a, dir_b)

        assert len(result.identical) >= 2  # shared.txt + deep.txt

    def test_modified_files(self, two_dirs):
        dir_a, dir_b = two_dirs
        result = compare_directories(dir_a, dir_b)

        assert len(result.modified) >= 1  # modified.txt

    def test_summary_text(self, two_dirs):
        dir_a, dir_b = two_dirs
        result = compare_directories(dir_a, dir_b)
        summary = result.summary_text()

        assert "Only in A" in summary
        assert "Only in B" in summary
        assert "Identical" in summary
        assert "Modified" in summary

    def test_empty_dirs(self, tmp_path):
        dir_a = tmp_path / "empty_a"
        dir_b = tmp_path / "empty_b"
        dir_a.mkdir()
        dir_b.mkdir()

        result = compare_directories(dir_a, dir_b)
        assert result.total_unique == 0

    def test_total_unique(self, two_dirs):
        dir_a, dir_b = two_dirs
        result = compare_directories(dir_a, dir_b)

        expected = (
            len(result.only_in_a)
            + len(result.only_in_b)
            + len(result.identical)
            + len(result.modified)
        )
        assert result.total_unique == expected
