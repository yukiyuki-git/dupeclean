"""File deduplication cleanup result module for DupeClean.

Standardized cleanup result format.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class CleanupOutcome:
    """Standardized cleanup outcome."""

    path: str
    action: str
    success: bool
    size: int = 0
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupResultV2:
    """Complete cleanup result."""

    operation_id: str
    outcomes: list[CleanupOutcome] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def total_outcomes(self) -> int:
        return len(self.outcomes)

    @property
    def success_count(self) -> int:
        return sum(1 for o in self.outcomes if o.success)

    @property
    def error_count(self) -> int:
        return sum(1 for o in self.outcomes if not o.success)

    @property
    def total_freed(self) -> int:
        return sum(o.size for o in self.outcomes if o.success)

    @property
    def freed_display(self) -> str:
        return format_size(self.total_freed)

    def add(self, outcome: CleanupOutcome) -> None:
        self.outcomes.append(outcome)


def format_cleanup_result_v2(result: CleanupResultV2) -> str:
    """Format cleanup result as text."""
    lines = [
        f"Cleanup Result: {result.operation_id}",
        f"  Total: {result.total_outcomes:,}",
        f"  Success: {result.success_count:,}",
        f"  Errors: {result.error_count:,}",
        f"  Freed: {result.freed_display}",
    ]

    if result.error_count > 0:
        lines.append("\n  Errors:")
        for o in result.outcomes:
            if not o.success:
                lines.append(f"    {o.path}: {o.error}")

    return "\n".join(lines)
