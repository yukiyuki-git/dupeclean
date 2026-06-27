"""Tests for DupeClean action definitions module."""

from __future__ import annotations

from dupeclean.action_defs import (
    BUILTIN_ACTIONS,
    CleanupActionDef,
    format_action,
    get_action,
    list_actions,
)


class TestGetAction:
    def test_delete(self):
        action = get_action("delete")
        assert action.name == "Delete"
        assert action.reversible is False

    def test_hardlink(self):
        action = get_action("hardlink")
        assert action.name == "Hardlink"
        assert action.reversible is True

    def test_unknown_falls_back(self):
        action = get_action("unknown")
        assert action.name == "Delete"


class TestListActions:
    def test_has_actions(self):
        actions = list_actions()
        assert len(actions) >= 4


class TestBuiltinActions:
    def test_all_exist(self):
        expected = {"delete", "hardlink", "move", "compress"}
        assert set(BUILTIN_ACTIONS.keys()) == expected


class TestFormatAction:
    def test_basic(self):
        action = get_action("delete")
        text = format_action(action)
        assert "Delete" in text
        assert "No" in text  # Not reversible


class TestCleanupActionDef:
    def test_defaults(self):
        action = CleanupActionDef(name="test", description="test", action_type="test")
        assert action.reversible is True
        assert action.requires_confirmation is True
