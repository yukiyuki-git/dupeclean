"""File deduplication cleanup actions for DupeClean.

Execute cleanup actions from dedup analysis.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size
from .utils import create_hardlink, safe_remove


@dataclass
class CleanupAction:
    """A cleanup action to execute."""

    action_type: str  # "delete", "hardlink", "move"
    source: Path
    target: Path | None = None
    reason: str = ""


@dataclass
class ActionResult:
    """Result of executing a cleanup action."""

    action: CleanupAction
    success: bool
    error: str = ""
    space_freed: int = 0


@dataclass
class CleanupExecutor:
    """Execute cleanup actions with safety checks."""

    dry_run: bool = True
    results: list[ActionResult] = field(default_factory=list)
    on_before: Callable[[CleanupAction], bool] | None = None
    on_after: Callable[[CleanupAction, bool], None] | None = None

    def execute(self, action: CleanupAction, file_size: int = 0) -> ActionResult:
        """Execute a single cleanup action."""
        if self.on_before and not self.on_before(action):
            return ActionResult(action=action, success=False, error="Cancelled by callback")

        if self.dry_run:
            result = ActionResult(
                action=action,
                success=True,
                space_freed=file_size,
            )
            self.results.append(result)
            return result

        success = False
        error = ""

        if action.action_type == "delete":
            success, error = safe_remove(action.source)
        elif action.action_type == "hardlink" and action.target:
            success, error = create_hardlink(action.target, action.source)

        result = ActionResult(
            action=action,
            success=success,
            error=error,
            space_freed=file_size if success else 0,
        )
        self.results.append(result)

        if self.on_after:
            self.on_after(action, success)

        return result

    def execute_batch(self, actions: list[tuple[CleanupAction, int]]) -> list[ActionResult]:
        """Execute multiple actions.

        Args:
            actions: List of (action, file_size) tuples.

        Returns:
            List of results.
        """
        return [self.execute(action, size) for action, size in actions]

    @property
    def total_freed(self) -> int:
        return sum(r.space_freed for r in self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if not r.success)


def format_action_result(result: ActionResult) -> str:
    """Format an action result as text."""
    status = "OK" if result.success else "FAILED"
    return f"[{status}] {result.action.action_type}: {result.action.source.name}"


def format_executor_stats(executor: CleanupExecutor) -> str:
    """Format executor statistics as text."""
    return (
        f"Cleanup: {len(executor.results)} actions "
        f"({executor.success_count} OK, "
        f"{executor.error_count} errors)\n"
        f"  Freed: {format_size(executor.total_freed)}"
    )
