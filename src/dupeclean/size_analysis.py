"""File size distribution analyzer for DupeClean.

Provides detailed breakdowns of file sizes:
- Size histogram (how many files in each size bucket)
- Largest directories
- Size growth patterns
- Compression potential estimation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DirInfo, FileInfo, format_size


@dataclass
class SizeBucket:
    """A size range bucket."""

    label: str
    min_size: int
    max_size: int
    files: list[FileInfo] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def size_display(self) -> str:
        return format_size(self.total_size)


# Size bucket definitions
SIZE_BUCKETS = [
    ("Empty (0 B)", 0, 1),
    ("Tiny (1-1KB)", 1, 1024),
    ("Small (1-64KB)", 1024, 65536),
    ("Medium (64KB-1MB)", 65536, 1048576),
    ("Large (1-16MB)", 1048576, 16777216),
    ("Huge (16-256MB)", 16777216, 268435456),
    ("Giant (256MB-1GB)", 268435456, 1073741824),
    ("Massive (>1GB)", 1073741824, 2**63),
]


def analyze_size_distribution(
    files: list[FileInfo],
) -> list[SizeBucket]:
    """Analyze file size distribution.

    Returns list of SizeBucket with files grouped by size range.
    """
    buckets = [
        SizeBucket(label=label, min_size=min_s, max_size=max_s)
        for label, min_s, max_s in SIZE_BUCKETS
    ]

    for fi in files:
        for bucket in buckets:
            if bucket.min_size <= fi.size < bucket.max_size:
                bucket.files.append(fi)
                break

    return buckets


@dataclass
class DirSizeInfo:
    """Size information for a directory."""

    path: Path
    total_size: int
    file_count: int
    depth: int


def get_largest_directories(dirs: dict[Path, DirInfo], n: int = 20) -> list[DirSizeInfo]:
    """Get the N largest directories by total size."""
    dir_sizes = [
        DirSizeInfo(
            path=path,
            total_size=info.total_size,
            file_count=info.file_count,
            depth=info.depth,
        )
        for path, info in dirs.items()
    ]
    dir_sizes.sort(key=lambda d: d.total_size, reverse=True)
    return dir_sizes[:n]


def estimate_compression_potential(
    files: list[FileInfo],
) -> dict[str, int]:
    """Estimate how much space could be saved by compression.

    Returns dict with category -> estimated_savings.
    """
    # Rough compression ratios by file type
    compressible_exts = {
        ".txt",
        ".log",
        ".csv",
        ".json",
        ".xml",
        ".html",
        ".css",
        ".js",
        ".py",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".md",
        ".rst",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".sql",
        ".sh",
        ".bat",
        ".ps1",
    }
    already_compressed_exts = {
        ".zip",
        ".gz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".mp3",
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".flac",
        ".ogg",
        ".pdf",
        ".docx",
        ".xlsx",
        ".pptx",
    }

    compressible_size = 0
    already_compressed_size = 0
    other_size = 0

    for fi in files:
        ext = fi.ext.lower()
        if ext in compressible_exts:
            compressible_size += fi.size
        elif ext in already_compressed_exts:
            already_compressed_size += fi.size
        else:
            other_size += fi.size

    # Estimate ~60% compression for text files
    estimated_savings = int(compressible_size * 0.6)

    return {
        "compressible": compressible_size,
        "already_compressed": already_compressed_size,
        "other": other_size,
        "estimated_savings": estimated_savings,
    }


def format_size_distribution(buckets: list[SizeBucket]) -> str:
    """Format size distribution as text."""
    total = sum(b.count for b in buckets)
    total_size = sum(b.total_size for b in buckets)

    lines = ["Size Distribution:", ""]

    max_count = max((b.count for b in buckets), default=1)
    bar_width = 30

    for bucket in buckets:
        if bucket.count == 0:
            continue
        pct = (bucket.count / total * 100) if total else 0
        bar_len = int(bucket.count / max_count * bar_width) if max_count > 0 else 0
        bar = "█" * bar_len + "░" * (bar_width - bar_len)
        lines.append(
            f"  {bucket.label:<25s} {bar} {bucket.count:>6,} ({pct:5.1f}%)  {bucket.size_display}"
        )

    lines.extend(
        [
            "",
            f"  Total: {total:,} files, {format_size(total_size)}",
        ]
    )

    return "\n".join(lines)
