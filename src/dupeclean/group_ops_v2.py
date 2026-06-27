"""File deduplication group operations v2 for DupeClean.

Enhanced group operations with advanced features.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo


@dataclass
class OperationV2:
    """An enhanced operation."""
    operation_id: str
    operation_type: str
    group_id: int
    files: list[FileInfo] = field(default_factory=list)
    status: str = "pending"
    result: dict = field(default_factory=dict)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)


@dataclass
class OperationsManagerV2:
    """Enhanced operations manager."""
    operations: list[OperationV2] = field(default_factory=list)

    def add(self, operation: OperationV2) -> None:
        self.operations.append(operation)

    @property
    def pending(self) -> list[OperationV2]:
        return [op for op in self.operations if op.status == "pending"]

    @property
    def completed(self) -> list[OperationV2]:
        return [op for op in self.operations if op.status == "completed"]

    @property
    def total_operations(self) -> int:
        return len(self.operations)


def create_operations_v2(
    groups: list[DuplicateGroup], op_type: str = "cleanup"
) -> OperationsManagerV2:
    """Create operations for groups."""
    manager = OperationsManagerV2()
    for g in groups:
        manager.add(OperationV2(
            operation_id=f"op_{g.group_id}",
            operation_type=op_type,
            group_id=g.group_id,
            files=g.files,
        ))
    return manager


def format_operations_v2(manager: OperationsManagerV2) -> str:
    """Format operations as text."""
    return (
        f"Operations: {manager.total_operations} total, "
        f"{len(manager.pending)} pending, "
        f"{len(manager.completed)} completed"
    )
