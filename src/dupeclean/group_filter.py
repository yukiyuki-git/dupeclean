"""File deduplication duplicate group filter for DupeClean.

Filter duplicate groups by various criteria.
"""

from __future__ import annotations

from collections.abc import Callable

from .models import DuplicateGroup


def filter_by_min_count(groups: list[DuplicateGroup], min_count: int) -> list[DuplicateGroup]:
    """Filter groups with at least min_count files."""
    return [g for g in groups if g.count >= min_count]


def filter_by_min_size(groups: list[DuplicateGroup], min_size: int) -> list[DuplicateGroup]:
    """Filter groups with file size >= min_size."""
    return [g for g in groups if g.file_size >= min_size]


def filter_by_max_size(groups: list[DuplicateGroup], max_size: int) -> list[DuplicateGroup]:
    """Filter groups with file size <= max_size."""
    return [g for g in groups if g.file_size <= max_size]


def filter_by_extension(groups: list[DuplicateGroup], ext: str) -> list[DuplicateGroup]:
    """Filter groups by file extension."""
    ext_lower = ext.lower().lstrip(".")
    return [g for g in groups if g.files and g.files[0].ext.lstrip(".").lower() == ext_lower]


def filter_by_min_waste(groups: list[DuplicateGroup], min_waste: int) -> list[DuplicateGroup]:
    """Filter groups with wasted space >= min_waste."""
    return [g for g in groups if g.wasted_space >= min_waste]


def filter_by_pattern(groups: list[DuplicateGroup], pattern: str) -> list[DuplicateGroup]:
    """Filter groups containing files matching a name pattern."""
    import fnmatch

    return [g for g in groups if any(fnmatch.fnmatch(f.path.name, pattern) for f in g.files)]


def chain_filters(
    groups: list[DuplicateGroup],
    *filters: Callable[[list[DuplicateGroup]], list[DuplicateGroup]],
) -> list[DuplicateGroup]:
    """Apply multiple filters in sequence."""
    result = groups
    for f in filters:
        result = f(result)
    return result


def format_filter_result(original: int, filtered: int, filter_name: str) -> str:
    """Format filter result as text."""
    return f"Filter '{filter_name}': {filtered}/{original} groups"
