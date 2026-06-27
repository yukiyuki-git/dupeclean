"""Tests for DupeClean file size distribution analyzer."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DirInfo, FileInfo
from dupeclean.size_analysis import (
    analyze_size_distribution,
    estimate_compression_potential,
    format_size_distribution,
    get_largest_directories,
)


def _fi(path: str, size: int) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestAnalyzeSizeDistribution:
    def test_basic_distribution(self):
        files = [
            _fi("/a.txt", 500),  # Tiny
            _fi("/b.txt", 5000),  # Small
            _fi("/c.bin", 500000),  # Medium
            _fi("/d.bin", 5000000),  # Large
        ]
        buckets = analyze_size_distribution(files)
        assert len(buckets) > 0

        # Each file should be in exactly one bucket
        total = sum(b.count for b in buckets)
        assert total == len(files)

    def test_empty_file(self):
        files = [_fi("/empty.txt", 0)]
        buckets = analyze_size_distribution(files)
        empty_bucket = next(b for b in buckets if "Empty" in b.label)
        assert empty_bucket.count == 1

    def test_large_file(self):
        files = [_fi("/huge.bin", 2 * 1024 * 1024 * 1024)]
        buckets = analyze_size_distribution(files)
        total = sum(b.count for b in buckets)
        assert total == 1

    def test_empty_list(self):
        buckets = analyze_size_distribution([])
        assert all(b.count == 0 for b in buckets)

    def test_all_same_size(self):
        files = [_fi(f"/f{i}.txt", 5000) for i in range(10)]
        buckets = analyze_size_distribution(files)
        total = sum(b.count for b in buckets)
        assert total == 10


class TestGetLargestDirectories:
    def test_returns_sorted(self):
        dirs = {
            Path("/a"): DirInfo(path=Path("/a"), total_size=1000, file_count=10),
            Path("/b"): DirInfo(path=Path("/b"), total_size=5000, file_count=20),
            Path("/c"): DirInfo(path=Path("/c"), total_size=2000, file_count=5),
        }
        result = get_largest_directories(dirs, n=2)
        assert len(result) == 2
        assert result[0].total_size == 5000
        assert result[1].total_size == 2000

    def test_n_greater_than_dirs(self):
        dirs = {
            Path("/a"): DirInfo(path=Path("/a"), total_size=100, file_count=1),
        }
        result = get_largest_directories(dirs, n=10)
        assert len(result) == 1


class TestEstimateCompressionPotential:
    def test_text_files(self):
        files = [_fi("/code.py", 10000)]
        result = estimate_compression_potential(files)
        assert result["compressible"] == 10000
        assert result["estimated_savings"] > 0

    def test_already_compressed(self):
        files = [_fi("/photo.jpg", 10000)]
        result = estimate_compression_potential(files)
        assert result["already_compressed"] == 10000
        assert result["estimated_savings"] == 0

    def test_mixed_files(self):
        files = [
            _fi("/code.py", 10000),
            _fi("/photo.jpg", 5000),
            _fi("/data.bin", 3000),
        ]
        result = estimate_compression_potential(files)
        assert result["compressible"] == 10000
        assert result["already_compressed"] == 5000
        assert result["other"] == 3000

    def test_empty_list(self):
        result = estimate_compression_potential([])
        assert result["compressible"] == 0


class TestFormatSizeDistribution:
    def test_contains_labels(self):
        files = [_fi("/a.txt", 500), _fi("/b.bin", 5000000)]
        buckets = analyze_size_distribution(files)
        text = format_size_distribution(buckets)
        assert "Size Distribution" in text
        assert "Total:" in text

    def test_shows_bars(self):
        files = [_fi(f"/f{i}.txt", 5000) for i in range(5)]
        buckets = analyze_size_distribution(files)
        text = format_size_distribution(buckets)
        assert "█" in text or "░" in text
