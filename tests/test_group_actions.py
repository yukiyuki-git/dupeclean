"""Tests for DupeClean group actions module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_actions import (
    ACTIONS,
    GroupAction,
    GroupActionResult,
    apply_action,
    format_group_actions,
    keep_first_action,
    keep_newest_action,
    keep_oldest_action,
    keep_shortest_action,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


def _group() -> DuplicateGroup:
    return DuplicateGroup(
        group_id=0,
        hash_value="abc",
        file_size=100,
        files=[
            _fi("/very/long/path/file.txt", 100, 100),
            _fi("/short/file.txt", 100, 200),
            _fi("/medium/path/file.txt", 100, 150),
        ],
    )


class TestKeepFirstAction:
    def test_basic(self):
        action = keep_first_action(_group())
        assert action.action_type == "keep_first"
        assert action.keeper_idx == 0
        assert len(action.files_to_remove) == 2


class TestKeepNewestAction:
    def test_basic(self):
        action = keep_newest_action(_group())
        assert action.keeper_idx == 1  # mtime=200


class TestKeepOldestAction:
    def test_basic(self):
        action = keep_oldest_action(_group())
        assert action.keeper_idx == 0  # mtime=100


class TestKeepShortestAction:
    def test_basic(self):
        action = keep_shortest_action(_group())
        assert action.keeper_idx == 1  # /short/file.txt


class TestApplyAction:
    def test_basic(self):
        groups = [_group()]
        result = apply_action(groups, "keep_first")
        assert result.total_actions == 1

    def test_unknown_action(self):
        groups = [_group()]
        result = apply_action(groups, "unknown")
        assert result.total_actions == 1  # Falls back to shortest


class TestActions:
    def test_all_exist(self):
        expected = {"keep_first", "keep_newest", "keep_oldest", "keep_shortest"}
        assert set(ACTIONS.keys()) == expected


class TestGroupActionResult:
    def test_total_saved(self):
        result = GroupActionResult(
            actions=[
                GroupAction(group_id=0, action_type="test", space_saved=100),
                GroupAction(group_id=1, action_type="test", space_saved=200),
            ]
        )
        assert result.total_saved == 300


class TestFormatGroupActions:
    def test_basic(self):
        result = GroupActionResult(
            actions=[
                GroupAction(group_id=0, action_type="test", space_saved=100),
            ]
        )
        text = format_group_actions(result)
        assert "1 groups" in text
