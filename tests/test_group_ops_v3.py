"""Tests for DupeClean group operations v3 module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_ops_v3 import (
    GroupOp,
    GroupOpsResult,
    create_keep_delete_ops,
    format_group_ops,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}", size, i * 100) for i in range(count)],
    )


class TestCreateKeepDeleteOps:
    def test_basic(self):
        groups = [_group(0, 100, 3)]
        ops = create_keep_delete_ops(groups)
        assert len(ops) == 2  # keep + delete
        assert ops[0].operation == "keep"
        assert ops[1].operation == "delete"
        assert len(ops[1].files) == 2

    def test_empty_groups(self):
        ops = create_keep_delete_ops([])
        assert len(ops) == 0

    def test_single_file_skipped(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a")],
            )
        ]
        ops = create_keep_delete_ops(groups)
        assert len(ops) == 0


class TestGroupOp:
    def test_file_count(self):
        op = GroupOp(group_id=0, operation="test", files=[_fi("/a"), _fi("/b")])
        assert op.file_count == 2


class TestGroupOpsResult:
    def test_total_ops(self):
        result = GroupOpsResult(
            operations=[
                GroupOp(group_id=0, operation="keep"),
                GroupOp(group_id=0, operation="delete"),
            ]
        )
        assert result.total_ops == 2


class TestFormatGroupOps:
    def test_basic(self):
        ops = [
            GroupOp(group_id=0, operation="keep"),
            GroupOp(group_id=0, operation="delete"),
        ]
        text = format_group_ops(ops)
        assert "1 keep" in text
        assert "1 delete" in text
