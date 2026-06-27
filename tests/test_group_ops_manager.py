"""Tests for DupeClean group operations manager."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_ops_manager import (
    GroupOperation,
    OperationsManager,
    create_operations,
    format_operations,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestOperationsManager:
    def test_add(self):
        mgr = OperationsManager()
        mgr.add(GroupOperation(group_id=0, operation="delete"))
        assert len(mgr.operations) == 1

    def test_pending(self):
        mgr = OperationsManager()
        mgr.add(GroupOperation(group_id=0, operation="delete", status="pending"))
        mgr.add(GroupOperation(group_id=1, operation="delete", status="completed"))
        assert len(mgr.pending) == 1

    def test_completed(self):
        mgr = OperationsManager()
        mgr.add(GroupOperation(group_id=0, operation="delete", status="pending"))
        mgr.add(GroupOperation(group_id=1, operation="delete", status="completed"))
        assert len(mgr.completed) == 1

    def test_total_impact(self):
        mgr = OperationsManager()
        mgr.add(GroupOperation(group_id=0, operation="delete", space_impact=100))
        mgr.add(GroupOperation(group_id=1, operation="delete", space_impact=200))
        assert mgr.total_impact == 300


class TestCreateOperations:
    def test_basic(self):
        groups = [_group(0, 100, 3), _group(1, 200, 2)]
        mgr = create_operations(groups, "delete")
        assert len(mgr.operations) == 2
        assert mgr.operations[0].files_affected == 2

    def test_default_operation(self):
        groups = [_group(0, 100, 2)]
        mgr = create_operations(groups)
        assert mgr.operations[0].operation == "delete"


class TestGroupOperation:
    def test_impact_display(self):
        op = GroupOperation(group_id=0, operation="delete", space_impact=1024)
        assert "B" in op.impact_display


class TestFormatOperations:
    def test_empty(self):
        mgr = OperationsManager()
        assert "No operations" in format_operations(mgr)

    def test_basic(self):
        mgr = OperationsManager()
        mgr.add(GroupOperation(group_id=0, operation="delete", space_impact=100))
        text = format_operations(mgr)
        assert "1 groups" in text
