"""Tests for DupeClean models."""

from pathlib import Path

from dupeclean.models import (
    DuplicateGroup,
    FileInfo,
    ScanStats,
    format_duration,
    format_size,
)


class TestFormatSize:
    def test_zero(self):
        assert format_size(0) == "0 B"

    def test_bytes(self):
        assert format_size(1) == "1 B"
        assert format_size(512) == "512 B"

    def test_kib(self):
        assert format_size(1024) == "1.0 KiB"

    def test_mib(self):
        assert format_size(1024 * 1024) == "1.0 MiB"

    def test_gib(self):
        assert format_size(1024 * 1024 * 1024) == "1.0 GiB"

    def test_tib(self):
        assert format_size(1024**4) == "1.0 TiB"

    def test_negative(self):
        assert format_size(-1) == "N/A"

    def test_decimal(self):
        result = format_size(1000, binary=False)
        assert "KB" in result

    def test_large(self):
        result = format_size(5 * 1024 * 1024 * 1024)
        assert "GiB" in result


class TestFormatDuration:
    def test_milliseconds(self):
        assert format_duration(0.5) == "500ms"

    def test_seconds(self):
        assert format_duration(5.5) == "5.5s"

    def test_minutes(self):
        assert format_duration(125) == "2m 5s"

    def test_hours(self):
        assert format_duration(3725) == "1h 2m"


class TestFileInfo:
    def test_from_path_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        fi = FileInfo.from_path(test_file)
        assert fi is not None
        assert fi.size == 11
        assert fi.ext == ".txt"
        assert not fi.is_dir

    def test_from_path_nonexistent(self, tmp_path):
        fi = FileInfo.from_path(tmp_path / "nonexistent.txt")
        assert fi is None

    def test_extension_property(self, tmp_path):
        test_file = tmp_path / "test.PY"
        test_file.write_bytes(b"x")
        fi = FileInfo.from_path(test_file)
        assert fi is not None
        assert fi.extension == "py"

    def test_size_display(self, tmp_path):
        test_file = tmp_path / "big.bin"
        test_file.write_bytes(b"\0" * 2048)
        fi = FileInfo.from_path(test_file)
        assert fi is not None
        assert "KiB" in fi.size_display

    def test_hash_for_dedup_none(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"x")
        fi = FileInfo.from_path(test_file)
        assert fi is not None
        assert fi.hash_for_dedup is None

    def test_hash_for_dedup_quick(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"x")
        fi = FileInfo.from_path(test_file)
        assert fi is not None
        fi.quick_hash = "abc123"
        assert fi.hash_for_dedup == "abc123"

    def test_hash_for_dedup_full_over_quick(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"x")
        fi = FileInfo.from_path(test_file)
        assert fi is not None
        fi.quick_hash = "abc"
        fi.full_hash = "def"
        assert fi.hash_for_dedup == "def"


class TestDuplicateGroup:
    def test_wasted_space(self):
        files = [FileInfo(path=Path(f"/a/file{i}.txt"), size=1000, mtime=0) for i in range(3)]
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=1000, files=files)
        assert group.wasted_space == 2000
        assert group.count == 3

    def test_wasted_space_single(self):
        files = [FileInfo(path=Path("/a/file.txt"), size=1000, mtime=0)]
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=1000, files=files)
        assert group.wasted_space == 0

    def test_size_display(self):
        files = [FileInfo(path=Path(f"/a/file{i}.txt"), size=1024, mtime=0) for i in range(2)]
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=1024, files=files)
        assert "KiB" in group.size_display


class TestScanStats:
    def test_unique_files(self):
        stats = ScanStats(total_files=10, duplicate_files=3)
        assert stats.unique_files == 7

    def test_dupe_percentage(self):
        stats = ScanStats(total_size=1000, wasted_space=200)
        assert stats.dupe_percentage == 20.0

    def test_dupe_percentage_zero_total(self):
        stats = ScanStats(total_size=0, wasted_space=0)
        assert stats.dupe_percentage == 0.0
