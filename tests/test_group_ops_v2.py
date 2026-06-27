"""Tests for DupeClean group operations v2 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_ops_v2 import (
    OperationsManagerV2,
    OperationV2,
    create_operations_v2,
    format_operations_v2,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid, hash_value=f"h{gid}", file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestOperationsManagerV2:
    def test_add(self):
        mgr = OperationsManagerV2()
        mgr.add(OperationV2(operation_id="1", operation_type="test", group_id=0))
        assert mgr.total_operations == 1

    def test_pending(self):
        mgr = OperationsManagerV2()
        mgr.add(OperationV2(operation_id="1", operation_type="test", group_id=0, status="pending"))
        mgr.add(OperationV2(operation_id="2", operation_type="test", group_id=1, status="completed"))
        assert len(mgr.pending) == 1

    def test_completed(self):
        mgr = OperationsManagerV2()
        mgr.add(OperationV2(operation_id="1", operation_type="test", group_id=0, status="pending"))
        mgr.add(OperationV2(operation_id="2", operation_type="test", group_id=1, status="completed"))
        assert len(mgr.completed) == 1


class TestCreateOperationsV2:
    def test_basic(self):
        groups = [_group(0, 100, 3), _group(1, 200, 2)]
        mgr = create_operations_v2(groups)
        assert mgr.total_operations == 2


class TestOperationV2:
    def test_file_count(self):
        op = OperationV2(operation_id="1", operation_type="test", group_id=0, files=[_fi("/a"), _fi("/b")])
        assert op.file_count == 2

    def test_total_size(self):
        op = OperationV2(operation_id="1", operation_type="test", group_id=0, files=[_fi("/a", 100), _fi("/b", 200)])
        assert op.total_size == 300


class TestFormatOperationsV2:
    def test_basic(self):
        mgr = OperationsManagerV2()
        mgr.add(OperationV2(operation_id="1", operation_type="test", group_id=0))
        text = format_operations_v2(mgr)
        assert "1 total" in text
