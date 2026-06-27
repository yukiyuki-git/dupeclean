"""File deduplication group operations for DupeClean.

Common operations on duplicate groups.
"""

from __future__ import annotations

from .models import DuplicateGroup, FileInfo, format_size


def merge_groups(groups: list[list[DuplicateGroup]]) -> list[DuplicateGroup]:
    """Merge multiple group lists into one."""
    merged = []
    for group_list in groups:
        merged.extend(group_list)
    return merged


def flatten_groups(groups: list[DuplicateGroup]) -> list[FileInfo]:
    """Extract all files from groups."""
    files = []
    for group in groups:
        files.extend(group.files)
    return files


def count_total_files(groups: list[DuplicateGroup]) -> int:
    """Count total files across all groups."""
    return sum(g.count for g in groups)


def count_total_waste(groups: list[DuplicateGroup]) -> int:
    """Calculate total wasted space."""
    return sum(g.wasted_space for g in groups)


def get_unique_extensions(groups: list[DuplicateGroup]) -> set[str]:
    """Get all unique file extensions in groups."""
    exts = set()
    for group in groups:
        for fi in group.files:
            exts.add(fi.ext)
    return exts


def get_group_sizes(groups: list[DuplicateGroup]) -> list[int]:
    """Get list of group sizes (file counts)."""
    return [g.count for g in groups]


def get_file_sizes(groups: list[DuplicateGroup]) -> list[int]:
    """Get list of file sizes from groups."""
    return [g.file_size for g in groups]


def split_by_size(
    groups: list[DuplicateGroup],
    threshold: int,
) -> tuple[list[DuplicateGroup], list[DuplicateGroup]]:
    """Split groups into large and small by file size."""
    large = [g for g in groups if g.file_size >= threshold]
    small = [g for g in groups if g.file_size < threshold]
    return large, small


def split_by_count(
    groups: list[DuplicateGroup],
    threshold: int,
) -> tuple[list[DuplicateGroup], list[DuplicateGroup]]:
    """Split groups into many and few by file count."""
    many = [g for g in groups if g.count >= threshold]
    few = [g for g in groups if g.count < threshold]
    return many, few


def format_group_summary(groups: list[DuplicateGroup]) -> str:
    """Format a summary of groups."""
    if not groups:
        return "No duplicate groups."

    total_waste = count_total_waste(groups)
    total_files = count_total_files(groups)
    extensions = get_unique_extensions(groups)

    return (
        f"Groups: {len(groups)}, "
        f"Files: {total_files:,}, "
        f"Wasted: {format_size(total_waste)}, "
        f"Extensions: {', '.join(sorted(extensions)[:5])}"
    )
