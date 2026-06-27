"""File deduplication cleanup strategy executor for DupeClean.

Execute cleanup strategies on groups.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class StrategyResultV2:
    """Result of executing a strategy."""

    strategy_name: str
    groups_processed: int = 0
    files_affected: int = 0
    space_saved: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def saved_display(self) -> str:
        return format_size(self.space_saved)


def execute_strategy_v2(
    groups: list[DuplicateGroup],
    strategy: str = "shortest",
    dry_run: bool = True,
) -> StrategyResultV2:
    """Execute a cleanup strategy on groups."""
    result = StrategyResultV2(strategy_name=strategy)

    for group in groups:
        if len(group.files) < 2:
            continue

        result.groups_processed += 1
        keep_idx = _select_keeper(group, strategy)

        for i, fi in enumerate(group.files):
            if i == keep_idx:
                continue
            result.files_affected += 1
            result.space_saved += fi.size

    return result


def _select_keeper(group: DuplicateGroup, strategy: str) -> int:
    if strategy == "newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))


def format_strategy_result_v2(result: StrategyResultV2) -> str:
    """Format strategy result as text."""
    return (
        f"Strategy '{result.strategy_name}': "
        f"{result.groups_processed} groups, "
        f"{result.files_affected} files affected, "
        f"{result.saved_display} saved"
    )
