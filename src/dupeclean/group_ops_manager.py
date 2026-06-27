"""File deduplication group operations manager for DupeClean.

Manage and coordinate group operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupOperation:
    """An operation on a group."""

    group_id: int
    operation: str  # "delete", "hardlink", "move", "compress"
    status: str = "pending"
    files_affected: int = 0
    space_impact: int = 0

    @property
    def impact_display(self) -> str:
        return format_size(self.space_impact)


@dataclass
class OperationsManager:
    """Manage group operations."""

    operations: list[GroupOperation] = field(default_factory=list)

    def add(self, operation: GroupOperation) -> None:
        self.operations.append(operation)

    @property
    def pending(self) -> list[GroupOperation]:
        return [op for op in self.operations if op.status == "pending"]

    @property
    def completed(self) -> list[GroupOperation]:
        return [op for op in self.operations if op.status == "completed"]

    @property
    def total_impact(self) -> int:
        return sum(op.space_impact for op in self.operations)

    @property
    def impact_display(self) -> str:
        return format_size(self.total_impact)


def create_operations(
    groups: list[DuplicateGroup],
    operation: str = "delete",
) -> OperationsManager:
    """Create operations for duplicate groups."""
    manager = OperationsManager()

    for group in groups:
        manager.add(
            GroupOperation(
                group_id=group.group_id,
                operation=operation,
                files_affected=group.count - 1,
                space_impact=group.wasted_space,
            )
        )

    return manager


def format_operations(manager: OperationsManager) -> str:
    """Format operations as text."""
    if not manager.operations:
        return "No operations."

    return (
        f"Operations: {len(manager.operations)} groups\n"
        f"  Pending: {len(manager.pending)}\n"
        f"  Completed: {len(manager.completed)}\n"
        f"  Impact: {manager.impact_display}"
    )
