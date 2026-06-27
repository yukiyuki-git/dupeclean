"""File deduplication file dedup engine for DupeClean.

Core deduplication engine combining all detection methods.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import format_size


@dataclass
class DedupConfig:
    """Configuration for dedup engine."""

    hash_algorithm: str = "xxhash"
    quick_hash_size: int = 4096
    medium_hash_size: int = 65536
    threads: int = 4
    use_prefilter: bool = True
    use_cache: bool = True


@dataclass
class DedupEngineResult:
    """Result of dedup engine run."""

    files_scanned: int = 0
    size_groups: int = 0
    hash_groups: int = 0
    confirmed_groups: int = 0
    total_duplicates: int = 0
    total_wasted: int = 0
    scan_duration: float = 0.0
    hash_duration: float = 0.0
    total_duration: float = 0.0

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)

    @property
    def dupe_percentage(self) -> float:
        if self.files_scanned == 0:
            return 0.0
        return (self.total_duplicates / self.files_scanned) * 100


def create_engine_config(
    fast: bool = False,
    thorough: bool = False,
) -> DedupConfig:
    """Create engine configuration preset."""
    if fast:
        return DedupConfig(
            hash_algorithm="xxhash",
            quick_hash_size=2048,
            threads=8,
            use_prefilter=True,
            use_cache=True,
        )
    if thorough:
        return DedupConfig(
            hash_algorithm="sha256",
            quick_hash_size=8192,
            medium_hash_size=131072,
            threads=4,
            use_prefilter=False,
        )
    return DedupConfig()


def format_engine_result(result: DedupEngineResult) -> str:
    """Format engine result as text."""
    lines = [
        "Dedup Engine Result:",
        f"  Files scanned: {result.files_scanned:,}",
        f"  Size groups: {result.size_groups:,}",
        f"  Hash groups: {result.hash_groups:,}",
        f"  Confirmed: {result.confirmed_groups:,}",
        f"  Duplicates: {result.total_duplicates:,}",
        f"  Wasted: {result.wasted_display} ({result.dupe_percentage:.1f}%)",
        f"  Scan: {result.scan_duration:.2f}s",
        f"  Hash: {result.hash_duration:.2f}s",
        f"  Total: {result.total_duration:.2f}s",
    ]
    return "\n".join(lines)
