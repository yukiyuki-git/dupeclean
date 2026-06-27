"""File deduplication cleanup runner for DupeClean.

Run cleanup operations with full lifecycle management.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .models import DuplicateGroup, format_size


@dataclass
class RunnerConfig:
    """Configuration for cleanup runner."""

    strategy: str = "shortest"
    dry_run: bool = True
    verify: bool = True
    max_errors: int = 100
    timeout: float = 3600.0


@dataclass
class RunnerResult:
    """Result of running cleanup."""

    success: bool = True
    files_processed: int = 0
    files_deleted: int = 0
    files_hardlinked: int = 0
    space_freed: int = 0
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0

    @property
    def freed_display(self) -> str:
        return format_size(self.space_freed)

    @property
    def success_rate(self) -> float:
        if self.files_processed == 0:
            return 0.0
        successful = self.files_deleted + self.files_hardlinked
        return successful / self.files_processed


def run_cleanup(
    groups: list[DuplicateGroup],
    config: RunnerConfig | None = None,
) -> RunnerResult:
    """Run cleanup operation.

    Args:
        groups: Duplicate groups to clean.
        config: Runner configuration.

    Returns:
        RunnerResult with operation details.
    """
    config = config or RunnerConfig()
    result = RunnerResult()
    start = time.monotonic()

    for group in groups:
        if len(group.files) < 2:
            continue

        keep_idx = _select_keeper(group, config.strategy)

        for i, fi in enumerate(group.files):
            if i == keep_idx:
                continue
            if config.dry_run:
                result.files_deleted += 1
                result.space_freed += fi.size
            result.files_processed += 1

    result.duration = time.monotonic() - start
    return result


def _select_keeper(group: DuplicateGroup, strategy: str) -> int:
    if strategy == "newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))


def format_runner_result(result: RunnerResult) -> str:
    """Format runner result as text."""
    return (
        f"Cleanup Result: "
        f"{result.files_processed} processed, "
        f"{result.files_deleted} deleted, "
        f"{result.files_hardlinked} hardlinked, "
        f"{result.freed_display} freed, "
        f"{result.duration:.1f}s"
    )
