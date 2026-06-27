"""File deduplication group indexer for DupeClean.

Index files within groups for fast lookups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, FileInfo


@dataclass
class GroupIndex:
    """Index of files across groups."""

    by_path: dict[str, tuple[int, FileInfo]] = field(
        default_factory=dict
    )  # path -> (group_id, FileInfo)
    by_hash: dict[str, list[int]] = field(default_factory=dict)  # hash -> [group_ids]
    by_size: dict[int, list[int]] = field(default_factory=dict)  # size -> [group_ids]
    by_ext: dict[str, list[int]] = field(default_factory=dict)  # ext -> [group_ids]

    def add_group(self, group: DuplicateGroup) -> None:
        """Add a group to the index."""
        for fi in group.files:
            self.by_path[str(fi.path)] = (group.group_id, fi)
            ext = fi.ext or "(none)"
            self.by_ext.setdefault(ext, []).append(group.group_id)
        self.by_size.setdefault(group.file_size, []).append(group.group_id)
        h = group.hash_value
        if h:
            self.by_hash.setdefault(h, []).append(group.group_id)

    def get_group_for_file(self, path: Path) -> int | None:
        """Get group ID for a file path."""
        entry = self.by_path.get(str(path))
        return entry[0] if entry else None

    def get_groups_by_ext(self, ext: str) -> list[int]:
        """Get group IDs by extension."""
        return self.by_ext.get(ext, [])

    def get_groups_by_size(self, size: int) -> list[int]:
        """Get group IDs by file size."""
        return self.by_size.get(size, [])

    @property
    def total_files(self) -> int:
        return len(self.by_path)

    @property
    def total_groups(self) -> int:
        return len(self.by_hash)


def build_group_index(
    groups: list[DuplicateGroup],
) -> GroupIndex:
    """Build an index from groups."""
    index = GroupIndex()
    for group in groups:
        index.add_group(group)
    return index


def format_group_index(index: GroupIndex) -> str:
    """Format index as text."""
    return (
        f"Group Index: {index.total_files} files, "
        f"{index.total_groups} groups, "
        f"{len(index.by_ext)} extensions"
    )
