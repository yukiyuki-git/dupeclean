"""File deduplication group splitter for DupeClean.

Split large groups into smaller manageable chunks.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import DuplicateGroup


@dataclass
class SplitResult:
    """Result of splitting groups."""

    original_groups: int = 0
    split_groups: int = 0
    splits_performed: int = 0

    @property
    def expansion(self) -> int:
        return self.split_groups - self.original_groups


def split_by_max_count(
    groups: list[DuplicateGroup],
    max_count: int = 10,
) -> tuple[list[DuplicateGroup], SplitResult]:
    """Split groups that have too many files.

    Args:
        groups: Groups to split.
        max_count: Maximum files per group.

    Returns:
        Tuple of (new_groups, result).
    """
    result = SplitResult(original_groups=len(groups))
    new_groups: list[DuplicateGroup] = []

    for group in groups:
        if group.count <= max_count:
            new_groups.append(group)
        else:
            # Split into chunks
            chunks = [group.files[i : i + max_count] for i in range(0, len(group.files), max_count)]
            for chunk in chunks:
                if len(chunk) >= 2:
                    new_groups.append(
                        DuplicateGroup(
                            group_id=len(new_groups),
                            hash_value=group.hash_value,
                            file_size=group.file_size,
                            files=chunk,
                        )
                    )
            result.splits_performed += 1

    result.split_groups = len(new_groups)
    return new_groups, result


def split_by_size_range(
    groups: list[DuplicateGroup],
    max_size: int = 100_000_000,
) -> tuple[list[DuplicateGroup], list[DuplicateGroup]]:
    """Split groups into large and small by file size.

    Returns:
        Tuple of (large_groups, small_groups).
    """
    large = [g for g in groups if g.file_size > max_size]
    small = [g for g in groups if g.file_size <= max_size]
    return large, small


def format_split_result(result: SplitResult) -> str:
    """Format split result as text."""
    return (
        f"Split: {result.original_groups} -> "
        f"{result.split_groups} groups "
        f"({result.splits_performed} splits)"
    )
