"""File deduplication cleanup queue processor for DupeClean.

Process cleanup queues with concurrency control.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class ProcessorConfig:
    """Configuration for queue processor."""

    max_workers: int = 1
    batch_size: int = 10
    timeout: float = 300.0
    retry_count: int = 3


@dataclass
class ProcessorResult:
    """Result of processing a queue batch."""

    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.processed == 0:
            return 0.0
        return self.succeeded / self.processed


class QueueProcessor:
    """Process cleanup queue items."""

    def __init__(self, config: ProcessorConfig | None = None) -> None:
        self.config = config or ProcessorConfig()
        self.results: list[ProcessorResult] = []

    def process_batch(
        self,
        items: list,
        handler: Callable[[object], bool],
    ) -> ProcessorResult:
        """Process a batch of items."""
        start = time.monotonic()
        result = ProcessorResult()

        for item in items[: self.config.batch_size]:
            result.processed += 1
            try:
                success = handler(item)
                if success:
                    result.succeeded += 1
                else:
                    result.failed += 1
            except Exception:
                result.failed += 1

        result.duration = time.monotonic() - start
        self.results.append(result)
        return result

    @property
    def total_processed(self) -> int:
        return sum(r.processed for r in self.results)

    @property
    def total_succeeded(self) -> int:
        return sum(r.succeeded for r in self.results)


def format_processor_result(result: ProcessorResult) -> str:
    """Format processor result as text."""
    return (
        f"Batch: {result.processed} processed, "
        f"{result.succeeded} OK, "
        f"{result.failed} failed, "
        f"{result.duration:.2f}s"
    )
