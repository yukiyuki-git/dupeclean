"""Duplicate directory finder for DupeClean.

Finds directories that have identical contents even if they
have different names or paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DirInfo, FileInfo, format_size


@dataclass
class DirFingerprint:
    """Content-based fingerprint for a directory."""

    path: Path
    file_count: int
    total_size: int
    content_hash: str  # Hash of all file hashes combined

    @property
    def size_display(self) -> str:
        return format_size(self.total_size)


@dataclass
class DuplicateDirGroup:
    """A group of directories with identical contents."""

    group_id: int
    fingerprint: DirFingerprint
    directories: list[DirFingerprint] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.directories)

    @property
    def wasted_space(self) -> int:
        return self.fingerprint.total_size * (self.count - 1)


def fingerprint_directory(
    dir_info: DirInfo,
    files: list[FileInfo],
) -> DirFingerprint | None:
    """Create a content fingerprint for a directory.

    Uses only direct children (not recursive).
    """
    direct_files = [f for f in files if f.path.parent == dir_info.path]
    if not direct_files:
        return None

    # Sort file hashes for deterministic comparison
    hashes = sorted(f.full_hash or f.quick_hash or str(f.size) for f in direct_files)
    content_hash = "|".join(hashes)

    return DirFingerprint(
        path=dir_info.path,
        file_count=len(direct_files),
        total_size=sum(f.size for f in direct_files),
        content_hash=content_hash,
    )


def find_duplicate_directories(
    dirs: dict[Path, DirInfo],
    files: list[FileInfo],
) -> list[DuplicateDirGroup]:
    """Find directories with identical contents.

    Args:
        dirs: Directory info map from scanner.
        files: Files list with hashes.

    Returns:
        List of DuplicateDirGroup sorted by wasted space.
    """
    # Group directories by file count and total size first
    size_groups: dict[tuple[int, int], list[DirInfo]] = {}
    for dir_info in dirs.values():
        if dir_info.file_count > 0:
            key = (dir_info.file_count, dir_info.total_size)
            size_groups.setdefault(key, []).append(dir_info)

    # Only check groups with multiple directories
    candidates = [group for group in size_groups.values() if len(group) >= 2]

    # Fingerprint candidates and group by content hash
    fingerprint_groups: dict[str, list[DirFingerprint]] = {}
    for group in candidates:
        for dir_info in group:
            fp = fingerprint_directory(dir_info, files)
            if fp:
                fingerprint_groups.setdefault(fp.content_hash, []).append(fp)

    # Build result groups
    results: list[DuplicateDirGroup] = []
    group_id = 0
    for _content_hash, fps in fingerprint_groups.items():
        if len(fps) >= 2:
            results.append(
                DuplicateDirGroup(
                    group_id=group_id,
                    fingerprint=fps[0],
                    directories=fps,
                )
            )
            group_id += 1

    results.sort(key=lambda g: g.wasted_space, reverse=True)
    return results


def format_duplicate_dirs(
    groups: list[DuplicateDirGroup],
) -> str:
    """Format duplicate directory results as text."""
    if not groups:
        return "No duplicate directories found."

    total_wasted = sum(g.wasted_space for g in groups)
    lines = [
        f"Duplicate directories: {len(groups)} groups, {format_size(total_wasted)} wasted",
        "",
    ]

    for group in groups[:20]:
        lines.append(
            f"  Group #{group.group_id}: "
            f"{group.count} dirs x "
            f"{group.fingerprint.size_display} "
            f"({group.fingerprint.file_count} files)"
        )
        for fp in group.directories:
            lines.append(f"    {fp.path}")

    return "\n".join(lines)
