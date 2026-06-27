"""Tests for DupeClean disk I/O benchmark."""

from __future__ import annotations

from dupeclean.iobench import (
    IOResult,
    benchmark_sequential_read,
    benchmark_sequential_write,
    benchmark_small_files,
    format_io_results,
    run_io_benchmark,
)


class TestIOResult:
    def test_mb_per_second(self):
        result = IOResult(
            name="test",
            duration=1.0,
            bytes_processed=1048576,
        )
        assert abs(result.mb_per_second - 1.0) < 0.01

    def test_ops_per_second(self):
        result = IOResult(
            name="test",
            duration=2.0,
            bytes_processed=2048,
            operations=100,
        )
        assert result.ops_per_second == 50.0

    def test_zero_duration(self):
        result = IOResult(
            name="test",
            duration=0.0,
            bytes_processed=1024,
        )
        assert result.mb_per_second == 0.0


class TestBenchmarkSequentialWrite:
    def test_basic(self, tmp_path):
        result = benchmark_sequential_write(tmp_path, size_mb=1)
        assert result.duration >= 0
        assert result.bytes_processed == 1048576

    def test_cleanup(self, tmp_path):
        benchmark_sequential_write(tmp_path, size_mb=1)
        test_file = tmp_path / ".dupeclean_io_test"
        assert not test_file.exists()


class TestBenchmarkSequentialRead:
    def test_basic(self, tmp_path):
        result = benchmark_sequential_read(tmp_path, size_mb=1)
        assert result.duration >= 0
        assert result.bytes_processed == 1048576


class TestBenchmarkSmallFiles:
    def test_basic(self, tmp_path):
        result = benchmark_small_files(tmp_path, count=50)
        assert result.operations == 50
        assert result.duration > 0

    def test_cleanup(self, tmp_path):
        benchmark_small_files(tmp_path, count=10)
        test_dir = tmp_path / ".dupeclean_io_test_dir"
        assert not test_dir.exists()


class TestRunIOBenchmark:
    def test_returns_results(self, tmp_path):
        results = run_io_benchmark(tmp_path)
        assert len(results) == 3


class TestFormatIOResults:
    def test_contains_all_tests(self, tmp_path):
        results = [
            IOResult(
                name="seq_write",
                duration=1.0,
                bytes_processed=1048576,
                operations=16,
            ),
            IOResult(
                name="seq_read",
                duration=0.5,
                bytes_processed=1048576,
                operations=16,
            ),
        ]
        text = format_io_results(results)
        assert "seq_write" in text
        assert "seq_read" in text
