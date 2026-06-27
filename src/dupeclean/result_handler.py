"""File deduplication cleanup result handler for DupeClean.

Handle and process cleanup results.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class ResultHandler:
    """Handle cleanup results."""

    results: list[dict] = field(default_factory=list)
    on_success: list[Callable] = field(default_factory=list)
    on_failure: list[Callable] = field(default_factory=list)

    def handle(self, result: dict) -> None:
        """Handle a cleanup result."""
        self.results.append(result)
        if result.get("success"):
            for callback in self.on_success:
                with contextlib.suppress(Exception):
                    callback(result)
        else:
            for callback in self.on_failure:
                with contextlib.suppress(Exception):
                    callback(result)

    def add_success_handler(self, callback: Callable) -> None:
        self.on_success.append(callback)

    def add_failure_handler(self, callback: Callable) -> None:
        self.on_failure.append(callback)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def successes(self) -> int:
        return sum(1 for r in self.results if r.get("success"))

    @property
    def failures(self) -> int:
        return sum(1 for r in self.results if not r.get("success"))


def format_handler_summary(handler: ResultHandler) -> str:
    """Format handler summary as text."""
    return f"Results: {handler.total} total, {handler.successes} success, {handler.failures} failed"
