"""Tests for DupeClean quick scan mode."""

from __future__ import annotations

import pytest

from dupeclean.quickscan import format_quick_scan_result, quick_scan


@pytest.fixture
def sample_dir(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"same content")
    (tmp_path / "b.txt").write_bytes(b"same content")
    (tmp_path / "c.txt").write_bytes(b"different")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.txt").write_bytes(b"same content")
    (sub / "e.bin").write_bytes(b"\x00" * 1024)
    return tmp_path


class TestQuickScan:
    def test_basic_scan(self, sample_dir):
        _files, stats, _groups = quick_scan(sample_dir)
        assert stats.total_files == 5
        assert stats.total_dirs >= 1

    def test_finds_size_duplicates(self, sample_dir):
        _files, _stats, groups = quick_scan(sample_dir)
        # a.txt, b.txt, d.txt all have same size
        assert len(groups) >= 1

    def test_wasted_space(self, sample_dir):
        _files, stats, _groups = quick_scan(sample_dir)
        assert stats.wasted_space > 0

    def test_groups_sorted_by_waste(self, sample_dir):
        _files, _stats, groups = quick_scan(sample_dir)
        for i in range(len(groups) - 1):
            assert groups[i].wasted_space >= groups[i + 1].wasted_space

    def test_empty_directory(self, tmp_path):
        _files, stats, groups = quick_scan(tmp_path)
        assert stats.total_files == 0
        assert len(groups) == 0

    def test_no_duplicates(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"a")
        (tmp_path / "b.txt").write_bytes(b"bb")
        (tmp_path / "c.txt").write_bytes(b"ccc")
        _files, _stats, groups = quick_scan(tmp_path)
        assert len(groups) == 0

    def test_single_file(self, tmp_path):
        (tmp_path / "only.txt").write_bytes(b"hello")
        _files, stats, groups = quick_scan(tmp_path)
        assert stats.total_files == 1
        assert len(groups) == 0


class TestFormatQuickScanResult:
    def test_contains_stats(self, sample_dir):
        files, stats, groups = quick_scan(sample_dir)
        text = format_quick_scan_result(sample_dir, files, stats, groups)
        assert "Quick scan:" in text
        assert "Files:" in text
        assert "Potential duplicates" in text

    def test_shows_groups(self, sample_dir):
        files, stats, groups = quick_scan(sample_dir)
        text = format_quick_scan_result(sample_dir, files, stats, groups)
        assert "Top potential duplicates" in text
