"""File deduplication cleanup rollback module for DupeClean.

Rollback cleanup operations when things go wrong.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RollbackAction:
    """An action to rollback."""

    action_type: str  # "restore", "recreate"
    source: Path
    backup: Path | None = None
    size: int = 0


@dataclass
class RollbackResult:
    """Result of a rollback operation."""

    actions_attempted: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.actions_attempted == 0:
            return 0.0
        return self.actions_succeeded / self.actions_attempted


class RollbackManager:
    """Manage cleanup rollback operations."""

    def __init__(self) -> None:
        self.actions: list[RollbackAction] = []
        self._executed = False

    def add_action(self, action: RollbackAction) -> None:
        """Add a rollback action."""
        self.actions.append(action)

    def execute(self) -> RollbackResult:
        """Execute all rollback actions."""
        result = RollbackResult()
        for action in self.actions:
            result.actions_attempted += 1
            try:
                if action.action_type == "restore" and action.backup:
                    if action.backup.exists():
                        import shutil

                        shutil.move(str(action.backup), str(action.source))
                        result.actions_succeeded += 1
                    else:
                        result.actions_failed += 1
                        result.errors.append(f"Backup not found: {action.backup}")
                else:
                    result.actions_failed += 1
            except OSError as e:
                result.actions_failed += 1
                result.errors.append(str(e))

        self._executed = True
        return result

    @property
    def action_count(self) -> int:
        return len(self.actions)

    @property
    def is_executed(self) -> bool:
        return self._executed


def format_rollback_result(result: RollbackResult) -> str:
    """Format rollback result as text."""
    return (
        f"Rollback: {result.actions_succeeded}/"
        f"{result.actions_attempted} succeeded"
        f" ({result.success_rate:.1%})"
    )
