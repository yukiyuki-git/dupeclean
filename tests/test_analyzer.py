"""Tests for DupeClean analyzer."""

import pytest

from dupeclean.analyzer import AnalysisResult, Analyzer


@pytest.fixture
def sample_tree(tmp_path):
    (tmp_path / "readme.md").write_text("# Test")
    (tmp_path / "main.py").write_bytes(b"print('hello')" * 100)
    (tmp_path / "data.bin").write_bytes(b"\0" * 4096)
    (tmp_path / "dup1.txt").write_bytes(b"duplicate content " * 50)
    (tmp_path / "dup2.txt").write_bytes(b"duplicate content " * 50)
    sub = tmp_path / "src"
    sub.mkdir()
    (sub / "app.py").write_bytes(b"print('app')" * 50)
    (sub / "lib.py").write_bytes(b"print('lib')" * 50)
    deep = sub / "utils"
    deep.mkdir()
    (deep / "helper.py").write_bytes(b"# helper" * 20)
    return tmp_path


class TestAnalyzer:
    def test_full_analysis(self, sample_tree):
        analyzer = Analyzer()
        result = analyzer.analyze(sample_tree, find_dupes=True)
        assert isinstance(result, AnalysisResult)
        assert result.stats.total_files == 8
        assert result.stats.total_size > 0

    def test_no_dedup(self, sample_tree):
        analyzer = Analyzer()
        result = analyzer.analyze(sample_tree, find_dupes=False)
        assert len(result.duplicates) == 0

    def test_with_dedup(self, sample_tree):
        analyzer = Analyzer()
        result = analyzer.analyze(sample_tree, find_dupes=True)
        assert len(result.duplicates) >= 1

    def test_summary_text(self, sample_tree):
        analyzer = Analyzer()
        result = analyzer.analyze(sample_tree)
        summary = result.summary_text()
        assert "Directory:" in summary
        assert "Total size:" in summary

    def test_top_extensions(self, sample_tree):
        analyzer = Analyzer()
        result = analyzer.analyze(sample_tree)
        exts = result.top_extensions
        assert len(exts) > 0

    def test_largest_files(self, sample_tree):
        analyzer = Analyzer()
        result = analyzer.analyze(sample_tree)
        largest = result.largest_files
        assert len(largest) > 0
        for i in range(len(largest) - 1):
            assert largest[i].size >= largest[i + 1].size

    def test_single_file(self, tmp_path):
        p = tmp_path / "single.txt"
        p.write_text("hello")
        analyzer = Analyzer()
        result = analyzer.analyze(p)
        assert result.stats.total_files == 1
        assert result.stats.total_size == 5
