"""File deduplication duplicate group manager v2 for DupeClean.

Enhanced group management with advanced features.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupManagerV2:
    """Enhanced group manager with advanced features."""

    groups: list[DuplicateGroup] = field(default_factory=list)

    def add(self, group: DuplicateGroup) -> None:
        self.groups.append(group)

    def remove(self, group_id: int) -> bool:
        before = len(self.groups)
        self.groups = [g for g in self.groups if g.group_id != group_id]
        return len(self.groups) < before

    def get(self, group_id: int) -> DuplicateGroup | None:
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None

    @property
    def count(self) -> int:
        return len(self.groups)

    @property
    def total_files(self) -> int:
        return sum(g.count for g in self.groups)

    @property
    def total_wasted(self) -> int:
        return sum(g.wasted_space for g in self.groups)

    @property
    def wasted_display(self) -> str:
        return format_size(self.total_wasted)

    def sort_by_size(self) -> None:
        self.groups.sort(key=lambda g: g.file_size, reverse=True)

    def sort_by_waste(self) -> None:
        self.groups.sort(key=lambda g: g.wasted_space, reverse=True)

    def sort_by_count(self) -> None:
        self.groups.sort(key=lambda g: g.count, reverse=True)

    def filter_min_size(self, min_size: int) -> list[DuplicateGroup]:
        return [g for g in self.groups if g.file_size >= min_size]

    def filter_extension(self, ext: str) -> list[DuplicateGroup]:
        return [g for g in self.groups if g.files and g.files[0].ext.lower() == ext.lower()]

    def get_top_wasted(self, n: int = 10) -> list[DuplicateGroup]:
        """Get top N groups by wasted space."""
        return sorted(self.groups, key=lambda g: g.wasted_space, reverse=True)[:n]

    def get_top_count(self, n: int = 10) -> list[DuplicateGroup]:
        """Get top N groups by file count."""
        return sorted(self.groups, key=lambda g: g.count, reverse=True)[:n]


def format_group_manager_v2(manager: GroupManagerV2) -> str:
    """Format group manager as text."""
    return (
        f"Groups: {manager.count}, Files: {manager.total_files:,}, Wasted: {manager.wasted_display}"
    )
