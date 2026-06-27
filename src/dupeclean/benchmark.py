"""Performance benchmarking module for DupeClean.

Measures and compares scan performance across different
configurations, algorithms, and directory sizes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .hasher import Hasher
from .models import FileInfo, HashStage
from .scanner import Scanner


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    name: str
    duration: float  # seconds
    items_processed: int = 0
    bytes_processed: int = 0
    extra: dict = field(default_factory=dict)

    @property
    def items_per_second(self) -> float:
        if self.duration <= 0:
            return 0.0
        return self.items_processed / self.duration

    @property
    def mb_per_second(self) -> float:
        if self.duration <= 0:
            return 0.0
        return (self.bytes_processed / 1048576) / self.duration

    @property
    def duration_display(self) -> str:
        if self.duration < 1:
            return f"{self.duration * 1000:.1f}ms"
        return f"{self.duration:.2f}s"


def benchmark_scan(
    path: Path,
    config: Config | None = None,
) -> BenchmarkResult:
    """Benchmark the file system scanner."""
    config = config or Config()
    scanner = Scanner(config.scanner)

    start = time.monotonic()
    files, dirs, stats = scanner.scan(path)
    duration = time.monotonic() - start

    return BenchmarkResult(
        name="scan",
        duration=duration,
        items_processed=len(files),
        bytes_processed=stats.total_size,
        extra={
            "dirs": len(dirs),
            "total_size": stats.total_size,
        },
    )


def benchmark_hash(
    files: list[FileInfo],
    stage: HashStage = HashStage.QUICK,
    config: Config | None = None,
    threads: int = 4,
) -> BenchmarkResult:
    """Benchmark file hashing."""
    config = config or Config()
    hasher = Hasher(config.hasher)
    total_bytes = sum(f.size for f in files)

    start = time.monotonic()
    hasher.hash_files(files, stage, threads)
    duration = time.monotonic() - start

    return BenchmarkResult(
        name=f"hash_{stage.value}",
        duration=duration,
        items_processed=len(files),
        bytes_processed=total_bytes,
        extra={"threads": threads, "stage": stage.value},
    )


def benchmark_hash_algorithms(
    files: list[FileInfo],
    algorithms: list[str] | None = None,
    stage: HashStage = HashStage.FULL,
) -> list[BenchmarkResult]:
    """Compare hashing performance across algorithms."""
    if algorithms is None:
        algorithms = ["xxhash", "md5", "sha256"]

    results = []
    for algo in algorithms:
        config = Config()
        config.hasher.algorithm = algo
        result = benchmark_hash(files, stage, config, threads=1)
        result.name = f"hash_{algo}"
        results.append(result)

    return results


def benchmark_thread_scaling(
    files: list[FileInfo],
    thread_counts: list[int] | None = None,
    config: Config | None = None,
) -> list[BenchmarkResult]:
    """Benchmark hash performance with different thread counts."""
    if thread_counts is None:
        thread_counts = [1, 2, 4, 8]

    results = []
    for threads in thread_counts:
        result = benchmark_hash(files, HashStage.QUICK, config, threads)
        result.name = f"threads_{threads}"
        results.append(result)

    return results


def format_benchmark(result: BenchmarkResult) -> str:
    """Format a benchmark result as text."""
    lines = [
        f"  {result.name}:",
        f"    Duration: {result.duration_display}",
        f"    Items: {result.items_processed:,}",
        f"    Throughput: {result.items_per_second:,.0f} items/s",
    ]
    if result.bytes_processed > 0:
        lines.append(f"    Bandwidth: {result.mb_per_second:.1f} MB/s")
    if result.extra:
        for key, value in result.extra.items():
            lines.append(f"    {key}: {value}")
    return "\n".join(lines)


def format_benchmark_comparison(
    results: list[BenchmarkResult],
) -> str:
    """Format multiple benchmark results for comparison."""
    if not results:
        return "  No benchmarks run."

    lines = ["Benchmark Results:", ""]

    # Header
    lines.append(f"  {'Name':<20s} {'Duration':>10s} {'Items/s':>12s} {'MB/s':>8s}")
    lines.append("  " + "-" * 55)

    for r in results:
        lines.append(
            f"  {r.name:<20s} {r.duration_display:>10s} "
            f"{r.items_per_second:>12,.0f} "
            f"{r.mb_per_second:>8.1f}"
        )

    return "\n".join(lines)
