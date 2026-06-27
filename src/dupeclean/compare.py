"""Directory comparison module for DupeClean.

Compare two directory trees and find:
- Files only in A
- Files only in B
- Files in both (with same/different content)
- Size differences
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .hasher import Hasher
from .models import FileInfo, HashStage, ScanStats, format_size
from .scanner import Scanner


@dataclass
class CompareResult:
    """Result of comparing two directory trees."""

    path_a: Path
    path_b: Path
    only_in_a: list[FileInfo] = field(default_factory=list)
    only_in_b: list[FileInfo] = field(default_factory=list)
    identical: list[tuple[FileInfo, FileInfo]] = field(default_factory=list)
    modified: list[tuple[FileInfo, FileInfo]] = field(default_factory=list)
    stats_a: ScanStats | None = None
    stats_b: ScanStats | None = None

    @property
    def total_unique(self) -> int:
        return len(self.only_in_a) + len(self.only_in_b) + len(self.identical) + len(self.modified)

    def summary_text(self) -> str:
        lines = [
            f"Comparing: {self.path_a} vs {self.path_b}",
            "",
            f"  Only in A:  {len(self.only_in_a):,} files",
            f"  Only in B:  {len(self.only_in_b):,} files",
            f"  Identical:  {len(self.identical):,} files",
            f"  Modified:   {len(self.modified):,} files",
        ]
        if self.stats_a:
            lines.append(f"\n  Size A: {format_size(self.stats_a.total_size)}")
        if self.stats_b:
            lines.append(f"  Size B: {format_size(self.stats_b.total_size)}")
        return "\n".join(lines)


def compare_directories(
    path_a: Path,
    path_b: Path,
    config: Config | None = None,
) -> CompareResult:
    """Compare two directory trees.

    Files are matched by relative path from their root.
    Matching files are then content-hashed to detect modifications.
    """
    config = config or Config()
    scanner = Scanner(config.scanner)

    files_a, _, stats_a = scanner.scan(path_a)
    files_b, _, stats_b = scanner.scan(path_b)

    # Build lookup by relative path
    def relative_map(root: Path, files: list[FileInfo]) -> dict[str, FileInfo]:
        result = {}
        for fi in files:
            try:
                rel = str(fi.path.relative_to(root))
            except ValueError:
                rel = fi.path.name
            result[rel] = fi
        return result

    map_a = relative_map(path_a, files_a)
    map_b = relative_map(path_b, files_b)

    keys_a = set(map_a.keys())
    keys_b = set(map_b.keys())

    only_a_keys = keys_a - keys_b
    only_b_keys = keys_b - keys_a
    common_keys = keys_a & keys_b

    result = CompareResult(
        path_a=path_a,
        path_b=path_b,
        stats_a=stats_a,
        stats_b=stats_b,
    )

    result.only_in_a = [map_a[k] for k in only_a_keys]
    result.only_in_b = [map_b[k] for k in only_b_keys]
    result.only_in_a.sort(key=lambda f: f.size, reverse=True)
    result.only_in_b.sort(key=lambda f: f.size, reverse=True)

    # Hash common files to detect identical vs modified
    common_a = [map_a[k] for k in common_keys]
    common_b = [map_b[k] for k in common_keys]

    hasher = Hasher(config.hasher)
    hasher.hash_files(common_a, HashStage.QUICK, config.scanner.threads)
    hasher.hash_files(common_b, HashStage.QUICK, config.scanner.threads)

    for key in common_keys:
        fa = map_a[key]
        fb = map_b[key]
        if fa.quick_hash and fb.quick_hash and fa.quick_hash == fb.quick_hash:
            result.identical.append((fa, fb))
        else:
            result.modified.append((fa, fb))

    result.identical.sort(key=lambda t: t[0].size, reverse=True)
    result.modified.sort(key=lambda t: t[0].size, reverse=True)

    return result
