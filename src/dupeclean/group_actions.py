"""File deduplication duplicate group actions module for DupeClean.

Define actions that can be taken on duplicate groups.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class GroupAction:
    """An action on a duplicate group."""

    group_id: int
    action_type: str  # "keep_first", "keep_newest", "keep_oldest", "keep_shortest"
    keeper_idx: int = 0
    files_to_remove: list[int] = field(default_factory=list)
    space_saved: int = 0

    @property
    def saved_display(self) -> str:
        return format_size(self.space_saved)


@dataclass
class GroupActionResult:
    """Result of applying group actions."""

    actions: list[GroupAction] = field(default_factory=list)

    @property
    def total_actions(self) -> int:
        return len(self.actions)

    @property
    def total_saved(self) -> int:
        return sum(a.space_saved for a in self.actions)


def keep_first_action(group: DuplicateGroup) -> GroupAction:
    """Keep the first file in the group."""
    return GroupAction(
        group_id=group.group_id,
        action_type="keep_first",
        keeper_idx=0,
        files_to_remove=list(range(1, group.count)),
        space_saved=group.file_size * (group.count - 1),
    )


def keep_newest_action(group: DuplicateGroup) -> GroupAction:
    """Keep the newest file in the group."""
    keep_idx = max(range(group.count), key=lambda i: group.files[i].mtime)
    return GroupAction(
        group_id=group.group_id,
        action_type="keep_newest",
        keeper_idx=keep_idx,
        files_to_remove=[i for i in range(group.count) if i != keep_idx],
        space_saved=group.file_size * (group.count - 1),
    )


def keep_oldest_action(group: DuplicateGroup) -> GroupAction:
    """Keep the oldest file in the group."""
    keep_idx = min(range(group.count), key=lambda i: group.files[i].mtime)
    return GroupAction(
        group_id=group.group_id,
        action_type="keep_oldest",
        keeper_idx=keep_idx,
        files_to_remove=[i for i in range(group.count) if i != keep_idx],
        space_saved=group.file_size * (group.count - 1),
    )


def keep_shortest_action(group: DuplicateGroup) -> GroupAction:
    """Keep the file with the shortest path."""
    keep_idx = min(range(group.count), key=lambda i: len(str(group.files[i].path)))
    return GroupAction(
        group_id=group.group_id,
        action_type="keep_shortest",
        keeper_idx=keep_idx,
        files_to_remove=[i for i in range(group.count) if i != keep_idx],
        space_saved=group.file_size * (group.count - 1),
    )


ACTIONS = {
    "keep_first": keep_first_action,
    "keep_newest": keep_newest_action,
    "keep_oldest": keep_oldest_action,
    "keep_shortest": keep_shortest_action,
}


def apply_action(
    groups: list[DuplicateGroup],
    action_name: str = "keep_shortest",
) -> GroupActionResult:
    """Apply an action to all groups."""
    action_fn = ACTIONS.get(action_name, keep_shortest_action)
    result = GroupActionResult()
    for group in groups:
        if len(group.files) >= 2:
            result.actions.append(action_fn(group))
    return result


def format_group_actions(result: GroupActionResult) -> str:
    """Format group actions as text."""
    return f"Actions: {result.total_actions} groups, {format_size(result.total_saved)} savings"
