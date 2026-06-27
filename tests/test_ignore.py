"""Tests for DupeClean ignore file support."""

from __future__ import annotations

from pathlib import Path

from dupeclean.ignore import (
    find_ignore_file,
    get_combined_ignore_patterns,
    load_ignore_patterns,
    should_ignore,
)


class TestLoadIgnorePatterns:
    def test_basic_patterns(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("# Comment\n*.log\nnode_modules/\n\n.git\n")
        patterns = load_ignore_patterns(ignore_file)
        assert patterns == ["*.log", "node_modules/", ".git"]

    def test_empty_file(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("")
        patterns = load_ignore_patterns(ignore_file)
        assert patterns == []

    def test_nonexistent_file(self, tmp_path):
        patterns = load_ignore_patterns(tmp_path / "nope")
        assert patterns == []

    def test_negation_skipped(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("*.log\n!important.log\n")
        patterns = load_ignore_patterns(ignore_file)
        assert patterns == ["*.log"]

    def test_comments_and_blanks(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("# keep\n\n  \n*.tmp\n# another comment\n")
        patterns = load_ignore_patterns(ignore_file)
        assert patterns == ["*.tmp"]


class TestFindIgnoreFile:
    def test_finds_in_directory(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("*.log")
        result = find_ignore_file(tmp_path)
        assert result == ignore_file

    def test_finds_in_parent(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("*.log")
        subdir = tmp_path / "sub" / "deep"
        subdir.mkdir(parents=True)
        result = find_ignore_file(subdir)
        assert result == ignore_file

    def test_not_found(self, tmp_path):
        result = find_ignore_file(tmp_path)
        assert result is None


class TestShouldIgnore:
    def test_filename_match(self):
        patterns = ["*.log"]
        assert should_ignore(Path("debug.log"), patterns) is True
        assert should_ignore(Path("code.py"), patterns) is False

    def test_directory_pattern(self):
        patterns = ["node_modules/"]
        assert should_ignore(Path("node_modules/package/index.js"), patterns) is True

    def test_specific_name(self):
        patterns = [".DS_Store"]
        assert should_ignore(Path(".DS_Store"), patterns) is True
        assert should_ignore(Path("file.txt"), patterns) is False

    def test_no_patterns(self):
        assert should_ignore(Path("anything.txt"), []) is False

    def test_relative_path_matching(self, tmp_path):
        patterns = ["build/*"]
        filepath = tmp_path / "build" / "output.js"
        assert should_ignore(filepath, patterns, root=tmp_path) is True


class TestGetCombinedIgnorePatterns:
    def test_config_only(self, tmp_path):
        patterns = get_combined_ignore_patterns(tmp_path, [".git", "node_modules"])
        assert ".git" in patterns
        assert "node_modules" in patterns

    def test_file_only(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("*.log\n")
        patterns = get_combined_ignore_patterns(tmp_path)
        assert "*.log" in patterns

    def test_combined(self, tmp_path):
        ignore_file = tmp_path / ".dupecleanignore"
        ignore_file.write_text("*.log\n")
        patterns = get_combined_ignore_patterns(tmp_path, [".git"])
        assert ".git" in patterns
        assert "*.log" in patterns
