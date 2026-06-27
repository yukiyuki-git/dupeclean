"""File deduplication duplicate group search for DupeClean.

Search within duplicate groups.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo


@dataclass
class GroupSearchResult:
    """Search result within groups."""

    matching_groups: list[DuplicateGroup] = field(default_factory=list)
    matching_files: list[tuple[int, FileInfo]] = field(default_factory=list)  # (group_id, file)

    @property
    def group_count(self) -> int:
        return len(self.matching_groups)

    @property
    def file_count(self) -> int:
        return len(self.matching_files)


def search_groups_by_filename(
    groups: list[DuplicateGroup],
    pattern: str,
) -> GroupSearchResult:
    """Search groups for files matching a filename pattern."""
    result = GroupSearchResult()

    for group in groups:
        group_matched = False
        for fi in group.files:
            if fnmatch.fnmatch(fi.path.name, pattern):
                result.matching_files.append((group.group_id, fi))
                group_matched = True
        if group_matched and group not in result.matching_groups:
            result.matching_groups.append(group)

    return result


def search_groups_by_extension(
    groups: list[DuplicateGroup],
    ext: str,
) -> GroupSearchResult:
    """Search groups for files with a specific extension."""
    ext_lower = ext.lower().lstrip(".")
    result = GroupSearchResult()

    for group in groups:
        if group.files and group.files[0].ext.lstrip(".").lower() == ext_lower:
            result.matching_groups.append(group)
            for fi in group.files:
                result.matching_files.append((group.group_id, fi))

    return result


def search_groups_by_path(
    groups: list[DuplicateGroup],
    path_pattern: str,
) -> GroupSearchResult:
    """Search groups for files matching a path pattern."""
    result = GroupSearchResult()

    for group in groups:
        group_matched = False
        for fi in group.files:
            if fnmatch.fnmatch(str(fi.path), path_pattern):
                result.matching_files.append((group.group_id, fi))
                group_matched = True
        if group_matched and group not in result.matching_groups:
            result.matching_groups.append(group)

    return result


def format_search_results(result: GroupSearchResult) -> str:
    """Format search results as text."""
    if result.group_count == 0:
        return "No matching groups found."

    return f"Search: {result.group_count} groups, {result.file_count} files"
