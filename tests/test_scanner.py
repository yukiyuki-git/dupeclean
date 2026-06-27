"""Tests for DupeClean scanner."""
from pathlib import Path
import pytest
from dupeclean.config import ScannerConfig
from dupeclean.scanner import Scanner


@pytest.fixture
def sample_dir(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    (tmp_path / "file2.txt").write_text("world")
    (tmp_path / "file3.py").write_bytes(b"\0" * 1024)
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "sub_file.txt").write_text("hello")
    (sub / "sub_file.dat").write_bytes(b"\0" * 2048)
    deep = sub / "deep"
    deep.mkdir()
    (deep / "deep_file.txt").write_bytes(b"\0" * 512)
    return tmp_path


class TestScanner:
    def test_scan_directory(self, sample_dir):
        scanner = Scanner()
        files, dirs, stats = scanner.scan(sample_dir)
        assert stats.total_files == 6
        assert stats.total_dirs >= 2
        assert stats.total_size > 0

    def test_scan_single_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")
        scanner = Scanner()
        files, dirs, stats = scanner.scan(test_file)
        assert stats.total_files == 1
        assert files[0].size == 5

    def test_scan_nonexistent(self, tmp_path):
        scanner = Scanner()
        with pytest.raises(FileNotFoundError):
            scanner.scan(tmp_path / "nonexistent")

    def test_ignore_patterns(self, sample_dir):
        config = ScannerConfig(ignore_patterns=["subdir"])
        scanner = Scanner(config)
        files, dirs, stats = scanner.scan(sample_dir)
        assert stats.total_files == 3

    def test_skip_hidden(self, tmp_path):
        (tmp_path / "visible.txt").write_text("v")
        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "secret.txt").write_text("s")
        config = ScannerConfig(skip_hidden=True)
        scanner = Scanner(config)
        files, dirs, stats = scanner.scan(tmp_path)
        assert stats.total_files == 1

    def test_files_have_extensions(self, sample_dir):
        scanner = Scanner()
        files, _, _ = scanner.scan(sample_dir)
        txt_files = [f for f in files if f.ext == ".txt"]
        assert len(txt_files) >= 2

    def test_directory_sizes(self, sample_dir):
        scanner = Scanner()
        _, dirs, _ = scanner.scan(sample_dir)
        root_info = dirs.get(sample_dir)
        assert root_info is not None
        assert root_info.total_size > 0

    def test_sorted_children(self, sample_dir):
        scanner = Scanner()
        _, dirs, _ = scanner.scan(sample_dir)
        children = scanner.get_sorted_children(sample_dir)
        assert len(children) > 0
