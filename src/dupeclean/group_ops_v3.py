"""File deduplication group operations v3 for DupeClean.

Advanced group operations with conflict resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo


@dataclass
class GroupOp:
    """A group operation."""

    group_id: int
    operation: str  # "keep", "delete", "hardlink", "move"
    files: list[FileInfo] = field(default_factory=list)
    result: dict = field(default_factory=dict)

    @property
    def file_count(self) -> int:
        return len(self.files)


@dataclass
class GroupOpsResult:
    """Result of group operations."""

    operations: list[GroupOp] = field(default_factory=list)

    @property
    def total_ops(self) -> int:
        return len(self.operations)

    @property
    def total_files(self) -> int:
        return sum(op.file_count for op in self.operations)


def create_keep_delete_ops(
    groups: list[DuplicateGroup],
    strategy: str = "shortest",
) -> list[GroupOp]:
    """Create keep/delete operations for groups."""
    ops: list[GroupOp] = []
    for group in groups:
        if len(group.files) < 2:
            continue
        keep_idx = _select(group, strategy)
        keep_files = [group.files[keep_idx]]
        delete_files = [f for i, f in enumerate(group.files) if i != keep_idx]
        ops.append(
            GroupOp(
                group_id=group.group_id,
                operation="keep",
                files=keep_files,
            )
        )
        ops.append(
            GroupOp(
                group_id=group.group_id,
                operation="delete",
                files=delete_files,
            )
        )
    return ops


def _select(group: DuplicateGroup, strategy: str) -> int:
    if strategy == "newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))


def format_group_ops(ops: list[GroupOp]) -> str:
    """Format operations as text."""
    keep = sum(1 for op in ops if op.operation == "keep")
    delete = sum(1 for op in ops if op.operation == "delete")
    return f"Operations: {keep} keep, {delete} delete"
