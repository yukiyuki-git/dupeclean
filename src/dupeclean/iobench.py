"""Disk I/O benchmark for DupeClean.

Measure read/write performance for different I/O patterns:
- Sequential read/write
- Random read/write
- Large file handling
- Small file handling
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IOResult:
    """Result of an I/O benchmark."""

    name: str
    duration: float  # seconds
    bytes_processed: int
    operations: int = 0

    @property
    def mb_per_second(self) -> float:
        if self.duration <= 0:
            return 0.0
        return (self.bytes_processed / 1048576) / self.duration

    @property
    def ops_per_second(self) -> float:
        if self.duration <= 0 or self.operations == 0:
            return 0.0
        return self.operations / self.duration


def benchmark_sequential_write(
    path: Path,
    size_mb: int = 100,
    block_size: int = 65536,
) -> IOResult:
    """Benchmark sequential write performance."""
    test_file = path / ".dupeclean_io_test"
    total_bytes = size_mb * 1048576
    block = b"\x00" * block_size
    blocks = total_bytes // block_size

    start = time.monotonic()
    try:
        with open(test_file, "wb") as f:
            for _ in range(blocks):
                f.write(block)
            f.flush()
            os.fsync(f.fileno())
    finally:
        test_file.unlink(missing_ok=True)

    duration = time.monotonic() - start
    return IOResult(
        name="seq_write",
        duration=duration,
        bytes_processed=total_bytes,
        operations=blocks,
    )


def benchmark_sequential_read(
    path: Path,
    size_mb: int = 100,
    block_size: int = 65536,
) -> IOResult:
    """Benchmark sequential read performance."""
    test_file = path / ".dupeclean_io_test"
    total_bytes = size_mb * 1048576
    block = b"\x00" * block_size
    blocks = total_bytes // block_size

    # Create test file
    with open(test_file, "wb") as f:
        for _ in range(blocks):
            f.write(block)

    # Read benchmark
    start = time.monotonic()
    try:
        with open(test_file, "rb") as f:
            while f.read(block_size):
                pass
    finally:
        test_file.unlink(missing_ok=True)

    duration = time.monotonic() - start
    return IOResult(
        name="seq_read",
        duration=duration,
        bytes_processed=total_bytes,
        operations=blocks,
    )


def benchmark_small_files(
    path: Path,
    count: int = 1000,
    file_size: int = 1024,
) -> IOResult:
    """Benchmark small file creation and reading."""
    test_dir = path / ".dupeclean_io_test_dir"
    test_dir.mkdir(exist_ok=True)
    data = b"x" * file_size

    # Write benchmark
    start = time.monotonic()
    try:
        for i in range(count):
            (test_dir / f"file_{i}.dat").write_bytes(data)
    finally:
        # Cleanup
        for f in test_dir.iterdir():
            f.unlink()
        test_dir.rmdir()

    duration = time.monotonic() - start
    return IOResult(
        name="small_files",
        duration=duration,
        bytes_processed=count * file_size,
        operations=count,
    )


def run_io_benchmark(path: Path) -> list[IOResult]:
    """Run all I/O benchmarks."""
    results = []
    results.append(benchmark_sequential_write(path, size_mb=50))
    results.append(benchmark_sequential_read(path, size_mb=50))
    results.append(benchmark_small_files(path, count=500))
    return results


def format_io_results(results: list[IOResult]) -> str:
    """Format I/O benchmark results as text."""
    lines = ["I/O Benchmark Results:", ""]
    lines.append(f"  {'Test':<15s} {'Duration':>8s} {'MB/s':>8s} {'ops/s':>10s}")
    lines.append("  " + "-" * 45)

    for r in results:
        duration_str = f"{r.duration:.2f}s" if r.duration >= 1 else f"{r.duration * 1000:.0f}ms"
        lines.append(
            f"  {r.name:<15s} {duration_str:>8s} {r.mb_per_second:>8.1f} {r.ops_per_second:>10,.0f}"
        )

    return "\n".join(lines)
