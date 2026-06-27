"""File deduplication cleanup action executor for DupeClean.

Execute individual cleanup actions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from .models import format_size


@dataclass
class ActionConfig:
    """Configuration for action execution."""

    dry_run: bool = True
    verify: bool = True
    backup: bool = True


@dataclass
class ActionResult:
    """Result of executing an action."""

    success: bool
    path: str
    action: str
    size: int = 0
    error: str = ""
    duration: float = 0.0

    @property
    def size_display(self) -> str:
        return format_size(self.size)


class ActionExecutor:
    """Execute cleanup actions."""

    def __init__(self, config: ActionConfig | None = None) -> None:
        self.config = config or ActionConfig()
        self.results: list[ActionResult] = []

    def execute(self, path: str, action: str, size: int = 0) -> ActionResult:
        """Execute a single action."""
        start = time.monotonic()

        result = ActionResult(
            success=True,
            path=path,
            action=action,
            size=size,
            duration=time.monotonic() - start,
        )
        self.results.append(result)
        return result

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def successes(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failures(self) -> int:
        return sum(1 for r in self.results if not r.success)


def format_action_result(result: ActionResult) -> str:
    """Format action result as text."""
    status = "OK" if result.success else "FAILED"
    return f"[{status}] {result.action}: {result.path} ({result.size_display})"
