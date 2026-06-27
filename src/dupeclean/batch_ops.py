"""File deduplication batch operations for DupeClean.

Execute batch operations on file groups.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .models import FileInfo


@dataclass
class BatchOperation:
    """A batch operation on files."""

    name: str
    files: list[FileInfo] = field(default_factory=list)
    action: Callable[[FileInfo], bool] | None = None
    results: list[bool] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)


@dataclass
class BatchResult:
    """Result of a batch operation."""

    operation: str
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.succeeded / self.total


def execute_batch(
    files: list[FileInfo],
    action: Callable[[FileInfo], tuple[bool, str]],
    name: str = "batch",
) -> BatchResult:
    """Execute an action on a batch of files.

    Args:
        files: Files to process.
        action: Function that returns (success, error_msg).
        name: Operation name.

    Returns:
        BatchResult with statistics.
    """
    import time

    start = time.monotonic()
    result = BatchResult(operation=name, total=len(files))

    for fi in files:
        success, error = action(fi)
        if success:
            result.succeeded += 1
        else:
            result.failed += 1
            if error:
                result.errors.append(f"{fi.path}: {error}")

    result.duration = time.monotonic() - start
    return result


def format_batch_result(result: BatchResult) -> str:
    """Format batch result as text."""
    lines = [
        f"Batch '{result.operation}':",
        f"  Total: {result.total:,}",
        f"  Succeeded: {result.succeeded:,}",
        f"  Failed: {result.failed:,}",
        f"  Skipped: {result.skipped:,}",
        f"  Duration: {result.duration:.2f}s",
        f"  Success rate: {result.success_rate:.1%}",
    ]
    if result.errors:
        lines.append(f"\n  Errors ({len(result.errors)}):")
        for err in result.errors[:5]:
            lines.append(f"    {err}")
    return "\n".join(lines)
