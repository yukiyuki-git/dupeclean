"""File deduplication configuration module for DupeClean.

Manage dedup-specific configuration settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DedupConfig:
    """Deduplication configuration."""

    # Hashing
    hash_algorithm: str = "xxhash"
    quick_hash_size: int = 4096
    medium_hash_size: int = 65536

    # Scanning
    follow_symlinks: bool = False
    skip_hidden: bool = False
    threads: int = 4
    ignore_patterns: list[str] = field(
        default_factory=lambda: [
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
        ]
    )

    # Strategy
    default_strategy: str = "shortest_path"
    dry_run: bool = True

    # Performance
    batch_size: int = 1000
    use_cache: bool = True
    use_prefilter: bool = True

    # Output
    report_format: str = "text"
    verbose: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "hash_algorithm": self.hash_algorithm,
            "quick_hash_size": self.quick_hash_size,
            "medium_hash_size": self.medium_hash_size,
            "follow_symlinks": self.follow_symlinks,
            "skip_hidden": self.skip_hidden,
            "threads": self.threads,
            "ignore_patterns": self.ignore_patterns,
            "default_strategy": self.default_strategy,
            "dry_run": self.dry_run,
            "batch_size": self.batch_size,
            "use_cache": self.use_cache,
            "use_prefilter": self.use_prefilter,
            "report_format": self.report_format,
            "verbose": self.verbose,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DedupConfig:
        """Create from dictionary."""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config


def create_fast_config() -> DedupConfig:
    """Create config optimized for speed."""
    return DedupConfig(
        hash_algorithm="xxhash",
        quick_hash_size=2048,
        threads=8,
        use_prefilter=True,
        use_cache=True,
        batch_size=2000,
    )


def create_thorough_config() -> DedupConfig:
    """Create config optimized for thoroughness."""
    return DedupConfig(
        hash_algorithm="sha256",
        quick_hash_size=8192,
        medium_hash_size=131072,
        threads=4,
        use_prefilter=False,
        use_cache=False,
    )


def create_balanced_config() -> DedupConfig:
    """Create balanced config."""
    return DedupConfig(
        hash_algorithm="xxhash",
        quick_hash_size=4096,
        medium_hash_size=65536,
        threads=4,
        use_prefilter=True,
        use_cache=True,
    )


def format_config(config: DedupConfig) -> str:
    """Format config as text."""
    lines = [
        "Dedup Configuration:",
        f"  Hash: {config.hash_algorithm} "
        f"(quick={config.quick_hash_size}, "
        f"medium={config.medium_hash_size})",
        f"  Threads: {config.threads}",
        f"  Strategy: {config.default_strategy}",
        f"  Follow symlinks: {config.follow_symlinks}",
        f"  Skip hidden: {config.skip_hidden}",
        f"  Use cache: {config.use_cache}",
        f"  Use prefilter: {config.use_prefilter}",
        f"  Batch size: {config.batch_size:,}",
        f"  Dry run: {config.dry_run}",
        f"  Report format: {config.report_format}",
        f"  Ignore: {', '.join(config.ignore_patterns)}",
    ]
    return "\n".join(lines)
