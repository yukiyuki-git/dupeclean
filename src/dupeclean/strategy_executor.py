"""File deduplication cleanup strategy executor for DupeClean.

Execute cleanup strategies on duplicate groups.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class StrategyExecution:
    """Execution of a cleanup strategy."""

    strategy_name: str
    groups_processed: int = 0
    files_processed: int = 0
    files_kept: int = 0
    files_removed: int = 0
    space_freed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)

    @property
    def success_rate(self) -> float:
        if self.files_processed == 0:
            return 0.0
        return (self.files_kept + self.files_removed) / self.files_processed


def execute_strategy(
    groups: list[DuplicateGroup],
    strategy: str = "shortest",
    dry_run: bool = True,
) -> StrategyExecution:
    """Execute a cleanup strategy on duplicate groups."""
    execution = StrategyExecution(strategy_name=strategy)

    for group in groups:
        if len(group.files) < 2:
            continue

        execution.groups_processed += 1
        keep_idx = _select_keeper(group, strategy)

        for i, fi in enumerate(group.files):
            execution.files_processed += 1
            if i == keep_idx:
                execution.files_kept += 1
            else:
                execution.files_removed += 1
                execution.space_freed += fi.size

    return execution


def _select_keeper(group: DuplicateGroup, strategy: str) -> int:
    if strategy == "newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))


def format_execution(execution: StrategyExecution) -> str:
    """Format execution as text."""
    return (
        f"Strategy '{execution.strategy_name}': "
        f"{execution.groups_processed} groups, "
        f"{execution.files_removed} removed, "
        f"{execution.freed_display} freed"
    )
