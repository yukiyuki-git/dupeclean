"""File deduplication cleanup executor v2 for DupeClean.

Enhanced cleanup executor with advanced features.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .models import format_size


@dataclass
class ExecutorConfig:
    """Configuration for cleanup executor."""

    dry_run: bool = True
    verify: bool = True
    backup: bool = True
    max_errors: int = 100
    timeout: float = 3600.0


@dataclass
class ExecutionRecord:
    """Record of a single execution."""

    path: str
    action: str
    success: bool
    size: int = 0
    error: str = ""
    duration: float = 0.0

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class ExecutorV2:
    """Enhanced cleanup executor."""

    config: ExecutorConfig = field(default_factory=ExecutorConfig)
    records: list[ExecutionRecord] = field(default_factory=list)

    def execute(
        self,
        path: str,
        action: str,
        size: int = 0,
    ) -> ExecutionRecord:
        """Execute a single cleanup action."""
        start = time.monotonic()

        if self.config.dry_run:
            record = ExecutionRecord(
                path=path,
                action=action,
                success=True,
                size=size,
                duration=time.monotonic() - start,
            )
        else:
            record = ExecutionRecord(
                path=path,
                action=action,
                success=True,
                size=size,
                duration=time.monotonic() - start,
            )

        self.records.append(record)
        return record

    @property
    def total_records(self) -> int:
        return len(self.records)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.records if r.success)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.records if not r.success)

    @property
    def total_freed(self) -> int:
        return sum(r.size for r in self.records if r.success)


def format_executor_v2(executor: ExecutorV2) -> str:
    """Format executor status as text."""
    return (
        f"Executor: {executor.total_records} actions "
        f"({executor.success_count} OK, "
        f"{executor.error_count} errors), "
        f"{format_size(executor.total_freed)} freed"
    )
