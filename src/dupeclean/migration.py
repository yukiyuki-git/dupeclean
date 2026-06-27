"""File migration module for DupeClean.

Move files between storage tiers based on usage patterns.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class MigrationRule:
    """A rule for file migration."""

    name: str
    source_pattern: str
    destination: Path
    max_age_days: float = 365
    min_size: int = 0
    max_size: int = 0


@dataclass
class MigrationAction:
    """A single migration action."""

    source: Path
    destination: Path
    reason: str
    size: int = 0


@dataclass
class MigrationPlan:
    """A complete migration plan."""

    actions: list[MigrationAction] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.actions)

    @property
    def total_size(self) -> int:
        return sum(a.size for a in self.actions)

    @property
    def total_size_display(self) -> str:
        return format_size(self.total_size)


def create_migration_plan(
    files: list[FileInfo],
    rule: MigrationRule,
) -> MigrationPlan:
    """Create a migration plan based on rules.

    Args:
        files: Files to evaluate.
        rule: Migration rule to apply.

    Returns:
        MigrationPlan with matching files.
    """
    import fnmatch
    import time

    plan = MigrationPlan()
    cutoff = time.time() - (rule.max_age_days * 86400)

    for fi in files:
        # Check pattern
        if not fnmatch.fnmatch(fi.path.name, rule.source_pattern):
            continue

        # Check age
        if rule.max_age_days > 0 and fi.mtime > cutoff:
            continue

        # Check size
        if rule.min_size > 0 and fi.size < rule.min_size:
            continue
        if rule.max_size > 0 and fi.size > rule.max_size:
            continue

        dest = rule.destination / fi.path.name
        plan.actions.append(
            MigrationAction(
                source=fi.path,
                destination=dest,
                reason=rule.name,
                size=fi.size,
            )
        )

    return plan


def execute_migration(
    plan: MigrationPlan,
    dry_run: bool = True,
) -> dict:
    """Execute a migration plan.

    Returns:
        Dict with succeeded, failed, errors.
    """
    succeeded = 0
    failed = 0
    errors: list[str] = []

    for action in plan.actions:
        if dry_run:
            succeeded += 1
            continue

        try:
            action.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(action.source), str(action.destination))
            succeeded += 1
        except OSError as e:
            failed += 1
            errors.append(f"{action.source}: {e}")

    return {
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors,
    }


def format_migration_plan(plan: MigrationPlan) -> str:
    """Format migration plan as text."""
    if not plan.actions:
        return "No files to migrate."

    lines = [
        f"Migration Plan: {plan.count} files, {plan.total_size_display}",
        "",
    ]

    for action in plan.actions[:20]:
        lines.append(f"  {action.source.name} -> {action.destination.parent} [{action.reason}]")

    if plan.count > 20:
        lines.append(f"\n  ... and {plan.count - 20} more files")

    return "\n".join(lines)
