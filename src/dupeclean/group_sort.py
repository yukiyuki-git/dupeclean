"""File deduplication duplicate group sort for DupeClean.

Sort duplicate groups by various criteria.
"""

from __future__ import annotations

from .models import DuplicateGroup


def sort_by_waste(groups: list[DuplicateGroup], reverse: bool = True) -> list[DuplicateGroup]:
    """Sort groups by wasted space."""
    return sorted(groups, key=lambda g: g.wasted_space, reverse=reverse)


def sort_by_count(groups: list[DuplicateGroup], reverse: bool = True) -> list[DuplicateGroup]:
    """Sort groups by file count."""
    return sorted(groups, key=lambda g: g.count, reverse=reverse)


def sort_by_size(groups: list[DuplicateGroup], reverse: bool = True) -> list[DuplicateGroup]:
    """Sort groups by file size."""
    return sorted(groups, key=lambda g: g.file_size, reverse=reverse)


def sort_by_group_id(groups: list[DuplicateGroup], reverse: bool = False) -> list[DuplicateGroup]:
    """Sort groups by group ID."""
    return sorted(groups, key=lambda g: g.group_id, reverse=reverse)


SORT_FUNCTIONS = {
    "waste": sort_by_waste,
    "count": sort_by_count,
    "size": sort_by_size,
    "id": sort_by_group_id,
}


def sort_groups(
    groups: list[DuplicateGroup],
    by: str = "waste",
    reverse: bool = True,
) -> list[DuplicateGroup]:
    """Sort groups by specified criterion."""
    fn = SORT_FUNCTIONS.get(by, sort_by_waste)
    return fn(groups, reverse=reverse)


def format_sort_info(
    groups: list[DuplicateGroup],
    sort_by: str,
) -> str:
    """Format sort info as text."""
    if not groups:
        return "No groups to sort."
    return f"Sorted {len(groups)} groups by {sort_by} ({'descending' if True else 'ascending'})"
