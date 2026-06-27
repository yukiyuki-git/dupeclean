"""Tests for DupeClean performance benchmarking."""

from __future__ import annotations

import pytest

from dupeclean.benchmark import (
    BenchmarkResult,
    benchmark_hash,
    benchmark_scan,
    format_benchmark,
    format_benchmark_comparison,
)
from dupeclean.models import FileInfo, HashStage


@pytest.fixture
def sample_files(tmp_path):
    files = []
    for i in range(20):
        p = tmp_path / f"file_{i}.bin"
        p.write_bytes(b"\x00" * (1024 * (i + 1)))
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)
    return files


class TestBenchmarkResult:
    def test_items_per_second(self):
        result = BenchmarkResult(name="test", duration=2.0, items_processed=100)
        assert result.items_per_second == 50.0

    def test_mb_per_second(self):
        result = BenchmarkResult(
            name="test",
            duration=1.0,
            bytes_processed=1048576,
        )
        assert abs(result.mb_per_second - 1.0) < 0.01

    def test_zero_duration(self):
        result = BenchmarkResult(name="test", duration=0.0, items_processed=100)
        assert result.items_per_second == 0.0
        assert result.mb_per_second == 0.0

    def test_duration_display_ms(self):
        result = BenchmarkResult(name="test", duration=0.5)
        assert "ms" in result.duration_display

    def test_duration_display_s(self):
        result = BenchmarkResult(name="test", duration=2.5)
        assert "s" in result.duration_display


class TestBenchmarkScan:
    def test_basic_benchmark(self, tmp_path, sample_files):
        result = benchmark_scan(tmp_path)
        assert result.name == "scan"
        assert result.duration >= 0
        assert result.items_processed > 0

    def test_returns_valid_result(self, tmp_path, sample_files):
        result = benchmark_scan(tmp_path)
        assert isinstance(result, BenchmarkResult)


class TestBenchmarkHash:
    def test_quick_hash(self, sample_files):
        result = benchmark_hash(sample_files, HashStage.QUICK, threads=1)
        assert result.name == "hash_quick"
        assert result.items_processed == len(sample_files)
        assert result.duration >= 0

    def test_multi_thread(self, sample_files):
        result = benchmark_hash(sample_files, HashStage.QUICK, threads=4)
        assert result.extra["threads"] == 4


class TestFormatBenchmark:
    def test_contains_name(self):
        result = BenchmarkResult(name="test_scan", duration=1.5, items_processed=100)
        text = format_benchmark(result)
        assert "test_scan" in text

    def test_contains_duration(self):
        result = BenchmarkResult(name="test", duration=2.0, items_processed=100)
        text = format_benchmark(result)
        assert "2.00s" in text

    def test_contains_throughput(self):
        result = BenchmarkResult(name="test", duration=1.0, items_processed=1000)
        text = format_benchmark(result)
        assert "1,000" in text


class TestFormatBenchmarkComparison:
    def test_empty_results(self):
        text = format_benchmark_comparison([])
        assert "No benchmarks" in text

    def test_multiple_results(self):
        results = [
            BenchmarkResult(
                name="hash_xxhash",
                duration=0.5,
                items_processed=100,
                bytes_processed=1024,
            ),
            BenchmarkResult(
                name="hash_md5",
                duration=1.0,
                items_processed=100,
                bytes_processed=1024,
            ),
        ]
        text = format_benchmark_comparison(results)
        assert "hash_xxhash" in text
        assert "hash_md5" in text
