"""File deduplication strategy module for DupeClean.

Different strategies for choosing which duplicate to keep.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import DuplicateGroup, FileInfo


@dataclass
class DedupDecision:
    """A decision about which file to keep in a duplicate group."""

    group_id: int
    keep: FileInfo
    remove: list[FileInfo]
    strategy: str
    reason: str


# Strategy functions
def keep_shortest_path(group: DuplicateGroup) -> DedupDecision:
    """Keep the file with the shortest path."""
    keep_idx = min(
        range(group.count),
        key=lambda i: len(str(group.files[i].path)),
    )
    return _make_decision(group, keep_idx, "shortest_path")


def keep_longest_path(group: DuplicateGroup) -> DedupDecision:
    """Keep the file with the longest path."""
    keep_idx = max(
        range(group.count),
        key=lambda i: len(str(group.files[i].path)),
    )
    return _make_decision(group, keep_idx, "longest_path")


def keep_newest(group: DuplicateGroup) -> DedupDecision:
    """Keep the newest file (most recent mtime)."""
    keep_idx = max(
        range(group.count),
        key=lambda i: group.files[i].mtime,
    )
    return _make_decision(group, keep_idx, "newest")


def keep_oldest(group: DuplicateGroup) -> DedupDecision:
    """Keep the oldest file."""
    keep_idx = min(
        range(group.count),
        key=lambda i: group.files[i].mtime,
    )
    return _make_decision(group, keep_idx, "oldest")


def keep_in_deepest_dir(group: DuplicateGroup) -> DedupDecision:
    """Keep the file in the deepest directory."""
    keep_idx = max(
        range(group.count),
        key=lambda i: len(group.files[i].path.parts),
    )
    return _make_decision(group, keep_idx, "deepest_dir")


def keep_in_shallowest_dir(group: DuplicateGroup) -> DedupDecision:
    """Keep the file in the shallowest directory."""
    keep_idx = min(
        range(group.count),
        key=lambda i: len(group.files[i].path.parts),
    )
    return _make_decision(group, keep_idx, "shallowest_dir")


def _make_decision(group: DuplicateGroup, keep_idx: int, strategy: str) -> DedupDecision:
    """Create a DedupDecision."""
    keep = group.files[keep_idx]
    remove = [f for i, f in enumerate(group.files) if i != keep_idx]
    return DedupDecision(
        group_id=group.group_id,
        keep=keep,
        remove=remove,
        strategy=strategy,
        reason=f"Strategy '{strategy}' selected {keep.path.name}",
    )


STRATEGIES = {
    "shortest_path": keep_shortest_path,
    "longest_path": keep_longest_path,
    "newest": keep_newest,
    "oldest": keep_oldest,
    "deepest_dir": keep_in_deepest_dir,
    "shallowest_dir": keep_in_shallowest_dir,
}


def apply_strategy(
    groups: list[DuplicateGroup],
    strategy_name: str = "shortest_path",
) -> list[DedupDecision]:
    """Apply a strategy to all duplicate groups."""
    strategy_fn = STRATEGIES.get(strategy_name, keep_shortest_path)
    return [strategy_fn(group) for group in groups]


def format_decisions(decisions: list[DedupDecision]) -> str:
    """Format dedup decisions as text."""
    if not decisions:
        return "No duplicate groups to process."

    total_remove = sum(len(d.remove) for d in decisions)
    lines = [
        f"Dedup Decisions: {len(decisions)} groups, {total_remove} files to remove",
        "",
    ]

    for d in decisions[:10]:
        lines.append(f"  Group #{d.group_id} [{d.strategy}]: KEEP {d.keep.path.name}")
        for f in d.remove:
            lines.append(f"    REMOVE {f.path.name}")

    if len(decisions) > 10:
        lines.append(f"\n  ... and {len(decisions) - 10} more groups")

    return "\n".join(lines)
