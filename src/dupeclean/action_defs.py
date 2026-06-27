"""File deduplication cleanup action module for DupeClean.

Define and manage cleanup actions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CleanupActionDef:
    """Definition of a cleanup action."""

    name: str
    description: str
    action_type: str  # "delete", "hardlink", "move", "compress"
    reversible: bool = True
    requires_confirmation: bool = True


# Built-in actions
BUILTIN_ACTIONS = {
    "delete": CleanupActionDef(
        name="Delete",
        description="Permanently delete duplicate files",
        action_type="delete",
        reversible=False,
        requires_confirmation=True,
    ),
    "hardlink": CleanupActionDef(
        name="Hardlink",
        description="Replace duplicates with hard links",
        action_type="hardlink",
        reversible=True,
        requires_confirmation=False,
    ),
    "move": CleanupActionDef(
        name="Move",
        description="Move duplicates to a holding directory",
        action_type="move",
        reversible=True,
        requires_confirmation=False,
    ),
    "compress": CleanupActionDef(
        name="Compress",
        description="Compress duplicate files",
        action_type="compress",
        reversible=True,
        requires_confirmation=False,
    ),
}


def get_action(name: str) -> CleanupActionDef:
    """Get an action by name."""
    return BUILTIN_ACTIONS.get(name, BUILTIN_ACTIONS["delete"])


def list_actions() -> list[CleanupActionDef]:
    """List all available actions."""
    return list(BUILTIN_ACTIONS.values())


def format_action(action: CleanupActionDef) -> str:
    """Format action as text."""
    rev = "Yes" if action.reversible else "No"
    confirm = "Yes" if action.requires_confirmation else "No"
    return (
        f"Action: {action.name}\n"
        f"  Description: {action.description}\n"
        f"  Type: {action.action_type}\n"
        f"  Reversible: {rev}\n"
        f"  Confirmation: {confirm}"
    )
