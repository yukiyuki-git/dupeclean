"""File deduplication cleanup optimizer for DupeClean.

Optimize cleanup operations for maximum efficiency.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class OptimizedPlan:
    """An optimized cleanup plan."""

    original_groups: int = 0
    optimized_actions: int = 0
    estimated_savings: int = 0
    optimizations: list[str] = field(default_factory=list)

    @property
    def savings_display(self) -> str:
        return format_size(self.estimated_savings)

    @property
    def efficiency_gain(self) -> float:
        if self.original_groups == 0:
            return 0.0
        return (self.optimized_actions / self.original_groups - 1) * 100


def optimize_cleanup(
    groups: list[DuplicateGroup],
) -> OptimizedPlan:
    """Optimize cleanup plan for efficiency.

    Optimizations:
    - Batch same-directory operations
    - Prioritize large savings
    - Skip tiny files (< 1KB)
    """
    plan = OptimizedPlan(original_groups=len(groups))

    # Sort by wasted space (largest first)
    sorted_groups = sorted(groups, key=lambda g: g.wasted_space, reverse=True)

    # Skip tiny files
    tiny_skipped = 0
    for group in sorted_groups:
        if group.file_size < 1024:
            tiny_skipped += 1
            continue
        plan.optimized_actions += group.count - 1
        plan.estimated_savings += group.wasted_space

    if tiny_skipped > 0:
        plan.optimizations.append(f"Skipped {tiny_skipped} groups with files < 1KB")

    return plan


def format_optimized_plan(plan: OptimizedPlan) -> str:
    """Format optimized plan as text."""
    lines = [
        "Optimized Plan:",
        f"  Original groups: {plan.original_groups}",
        f"  Optimized actions: {plan.optimized_actions}",
        f"  Estimated savings: {plan.savings_display}",
    ]
    if plan.optimizations:
        lines.append("\n  Optimizations:")
        for opt in plan.optimizations:
            lines.append(f"    - {opt}")
    return "\n".join(lines)
