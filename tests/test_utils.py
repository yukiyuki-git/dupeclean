"""Tests for DupeClean utils."""
import sys
from pathlib import Path
import pytest
from dupeclean.utils import (
    create_hardlink, get_file_extension, human_count, is_hidden,
    is_same_file, matches_pattern, safe_remove, safe_rmdir, safe_stat, truncate_path,
)


class TestIsHidden:
    def test_dotfile(self, tmp_path):
        p = tmp_path / ".hidden"
        p.touch()
        assert is_hidden(p) is True

    def test_regular_file(self, tmp_path):
        p = tmp_path / "visible.txt"
        p.touch()
        assert is_hidden(p) is False

    def test_dot_dot(self):
        assert is_hidden(Path("..")) is False


class TestMatchesPattern:
    def test_exact_match(self):
        assert matches_pattern(".git", [".git"]) is True

    def test_no_match(self):
        assert matches_pattern("src", [".git", "node_modules"]) is False

    def test_wildcard(self):
        assert matches_pattern("test.pyc", ["*.pyc"]) is True

    def test_empty_patterns(self):
        assert matches_pattern("anything", []) is False


class TestSafeStat:
    def test_existing_file(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("x")
        st = safe_stat(p)
        assert st is not None
        assert st.st_size == 1

    def test_nonexistent(self, tmp_path):
        st = safe_stat(tmp_path / "nonexistent")
        assert st is None


class TestIsSameFile:
    def test_same_file(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("x")
        assert is_same_file(p, p) is True

    def test_different_files(self, tmp_path):
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        a.write_text("x")
        b.write_text("x")
        assert is_same_file(a, b) is False


class TestGetFileExtension:
    def test_with_dot(self):
        assert get_file_extension(Path("test.txt")) == "txt"

    def test_no_extension(self):
        assert get_file_extension(Path("Makefile")) == ""

    def test_uppercase(self):
        assert get_file_extension(Path("test.PY")) == "py"

    def test_multiple_dots(self):
        assert get_file_extension(Path("archive.tar.gz")) == "gz"


class TestTruncatePath:
    def test_short_path(self):
        assert truncate_path("/a/b/c") == "/a/b/c"

    def test_long_path(self):
        result = truncate_path("/very/long/nested/directory/structure/file.txt", max_len=30)
        assert isinstance(result, str)


class TestHumanCount:
    def test_small(self):
        assert human_count(42) == "42"

    def test_thousands(self):
        assert human_count(1234) == "1,234"

    def test_millions(self):
        assert human_count(1234567) == "1,234,567"


class TestSafeRemove:
    def test_remove_file(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("x")
        success, _ = safe_remove(p)
        assert success is True
        assert not p.exists()

    def test_remove_nonexistent(self, tmp_path):
        success, _ = safe_remove(tmp_path / "nonexistent")
        assert success is True

    def test_remove_directory_fails(self, tmp_path):
        d = tmp_path / "dir"
        d.mkdir()
        success, _ = safe_remove(d)
        assert success is False


class TestSafeRmdir:
    def test_remove_empty_dir(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()
        success, _ = safe_rmdir(d)
        assert success is True

    def test_remove_nonempty_dir(self, tmp_path):
        d = tmp_path / "notempty"
        d.mkdir()
        (d / "file.txt").write_text("x")
        success, _ = safe_rmdir(d)
        assert success is False


class TestCreateHardlink:
    def test_create_hardlink(self, tmp_path):
        src = tmp_path / "source.txt"
        src.write_text("hello")
        dst = tmp_path / "link.txt"
        success, _ = create_hardlink(src, dst)
        assert success is True
        assert dst.exists()
        assert is_same_file(src, dst)

    def test_hardlink_overwrite(self, tmp_path):
        src = tmp_path / "source.txt"
        src.write_text("new")
        dst = tmp_path / "existing.txt"
        dst.write_text("old")
        success, _ = create_hardlink(src, dst)
        assert success is True
        assert dst.read_text() == "new"
