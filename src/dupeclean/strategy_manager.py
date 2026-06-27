"""File deduplication cleanup strategy module for DupeClean.

Define and manage cleanup strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class Strategy:
    """A cleanup strategy."""
    name: str
    description: str
    select_keeper: str  # "shortest", "newest", "oldest", "deepest", "shallowest"
    action: str = "hardlink"  # "hardlink", "delete"


@dataclass
class StrategyResult:
    """Result of applying a strategy to a group."""
    group_id: int
    strategy: str
    keeper: FileInfo
    to_remove: list[FileInfo] = field(default_factory=list)
    savings: int = 0


# Built-in strategies
STRATEGIES = {
    "shortest": Strategy(
        name="Shortest Path",
        description="Keep file with shortest path (most likely original)",
        select_keeper="shortest",
    ),
    "newest": Strategy(
        name="Newest",
        description="Keep most recently modified file",
        select_keeper="newest",
    ),
    "oldest": Strategy(
        name="Oldest",
        description="Keep oldest file (first created)",
        select_keeper="oldest",
    ),
    "deepest": Strategy(
        name="Deepest",
        description="Keep file in deepest directory",
        select_keeper="deepest",
    ),
    "shallowest": Strategy(
        name="Shallowest",
        description="Keep file in shallowest directory",
        select_keeper="shallowest",
    ),
}


def apply_strategy(
    group: DuplicateGroup,
    strategy_name: str = "shortest",
) -> StrategyResult:
    """Apply a strategy to a duplicate group."""
    strategy = STRATEGIES.get(strategy_name, STRATEGIES["shortest"])

    if strategy.select_keeper == "shortest":
        keep_idx = min(range(group.count), key=lambda i: len(str(group.files[i].path)))
    elif strategy.select_keeper == "newest":
        keep_idx = max(range(group.count), key=lambda i: group.files[i].mtime)
    elif strategy.select_keeper == "oldest":
        keep_idx = min(range(group.count), key=lambda i: group.files[i].mtime)
    elif strategy.select_keeper == "deepest":
        keep_idx = max(range(group.count), key=lambda i: len(group.files[i].path.parts))
    else:
        keep_idx = min(range(group.count), key=lambda i: len(group.files[i].path.parts))

    keeper = group.files[keep_idx]
    to_remove = [f for i, f in enumerate(group.files) if i != keep_idx]

    return StrategyResult(
        group_id=group.group_id,
        strategy=strategy.name,
        keeper=keeper,
        to_remove=to_remove,
        savings=sum(f.size for f in to_remove),
    )


def apply_strategy_to_all(
    groups: list[DuplicateGroup],
    strategy_name: str = "shortest",
) -> list[StrategyResult]:
    """Apply strategy to all groups."""
    return [apply_strategy(g, strategy_name) for g in groups]


def format_strategy_results(results: list[StrategyResult]) -> str:
    """Format strategy results as text."""
    if not results:
        return "No groups to process."

    total_savings = sum(r.savings for r in results)
    lines = [
        f"Strategy Results: {len(results)} groups, "
        f"{format_size(total_savings)} savings",
        "",
    ]

    for r in results[:10]:
        lines.append(
            f"  Group #{r.group_id} [{r.strategy}]: "
            f"KEEP {r.keeper.path.name}"
        )
        for f in r.to_remove[:3]:
            lines.append(f"    REMOVE {f.path.name}")

    return "\n".join(lines)
