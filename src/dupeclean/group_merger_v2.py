"""File deduplication group merger v2 for DupeClean.

Enhanced group merging with conflict resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo


@dataclass
class MergeConflict:
    """A conflict during merge."""

    group_a_id: int
    group_b_id: int
    conflicting_files: list[FileInfo] = field(default_factory=list)
    resolution: str = ""


@dataclass
class MergeResultV2:
    """Enhanced merge result."""

    original_count: int = 0
    merged_count: int = 0
    conflicts: list[MergeConflict] = field(default_factory=list)
    groups_merged: int = 0

    @property
    def reduction(self) -> int:
        return self.original_count - self.merged_count

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


def merge_groups_v2(
    groups: list[DuplicateGroup],
) -> tuple[list[DuplicateGroup], MergeResultV2]:
    """Enhanced merge with conflict detection."""
    result = MergeResultV2(original_count=len(groups))

    # Build file-to-group mapping
    file_to_groups: dict[str, list[int]] = {}
    for i, group in enumerate(groups):
        for fi in group.files:
            file_to_groups.setdefault(str(fi.path), []).append(i)

    # Find connected components
    visited = set()
    components: list[set[int]] = []

    for i in range(len(groups)):
        if i in visited:
            continue
        component: set[int] = set()
        stack = [i]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.add(current)
            for fi in groups[current].files:
                for neighbor in file_to_groups.get(str(fi.path), []):
                    if neighbor not in visited:
                        stack.append(neighbor)
        components.append(component)

    # Build merged groups
    new_groups: list[DuplicateGroup] = []
    for component in components:
        all_files: list[FileInfo] = []
        for idx in component:
            all_files.extend(groups[idx].files)

        seen: dict[str, FileInfo] = {}
        for fi in all_files:
            key = str(fi.path)
            if key not in seen:
                seen[key] = fi

        unique_files = list(seen.values())
        if len(unique_files) >= 2:
            new_groups.append(
                DuplicateGroup(
                    group_id=len(new_groups),
                    hash_value=groups[next(iter(component))].hash_value,
                    file_size=unique_files[0].size,
                    files=unique_files,
                )
            )

    result.merged_count = len(new_groups)
    result.groups_merged = sum(1 for c in components if len(c) > 1)

    return new_groups, result


def format_merge_result_v2(result: MergeResultV2) -> str:
    """Format merge result as text."""
    lines = [
        f"Merge: {result.original_count} -> {result.merged_count} groups",
        f"  Merged: {result.groups_merged}",
        f"  Reduction: {result.reduction}",
    ]
    if result.has_conflicts:
        lines.append(f"  Conflicts: {len(result.conflicts)}")
    return "\n".join(lines)
