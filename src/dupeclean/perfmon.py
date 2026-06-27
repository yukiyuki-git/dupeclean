"""File deduplication performance module for DupeClean.

Performance monitoring and optimization for dedup operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class PerformanceMetric:
    """A single performance measurement."""

    name: str
    duration: float
    items_processed: int = 0
    bytes_processed: int = 0

    @property
    def items_per_second(self) -> float:
        if self.duration <= 0:
            return 0.0
        return self.items_processed / self.duration

    @property
    def mb_per_second(self) -> float:
        if self.duration <= 0:
            return 0.0
        return (self.bytes_processed / 1048576) / self.duration


@dataclass
class PerformanceTracker:
    """Track performance metrics across operations."""

    metrics: list[PerformanceMetric] = field(default_factory=list)
    _start_times: dict[str, float] = field(default_factory=dict)

    def start(self, name: str) -> None:
        """Start timing an operation."""
        self._start_times[name] = time.monotonic()

    def stop(
        self,
        name: str,
        items: int = 0,
        bytes_count: int = 0,
    ) -> PerformanceMetric:
        """Stop timing and record metric."""
        start = self._start_times.pop(name, time.monotonic())
        duration = time.monotonic() - start
        metric = PerformanceMetric(
            name=name,
            duration=duration,
            items_processed=items,
            bytes_processed=bytes_count,
        )
        self.metrics.append(metric)
        return metric

    def get_metric(self, name: str) -> PerformanceMetric | None:
        """Get the most recent metric by name."""
        for m in reversed(self.metrics):
            if m.name == name:
                return m
        return None

    def total_duration(self) -> float:
        """Total duration of all operations."""
        return sum(m.duration for m in self.metrics)

    def summary(self) -> dict:
        """Get performance summary."""
        return {
            "total_operations": len(self.metrics),
            "total_duration": self.total_duration(),
            "metrics": {
                m.name: {
                    "duration": m.duration,
                    "items_per_second": m.items_per_second,
                    "mb_per_second": m.mb_per_second,
                }
                for m in self.metrics
            },
        }


def format_performance(tracker: PerformanceTracker) -> str:
    """Format performance metrics as text."""
    if not tracker.metrics:
        return "No performance metrics recorded."

    lines = [
        f"Performance Summary "
        f"({len(tracker.metrics)} operations, "
        f"{tracker.total_duration():.2f}s total):",
        "",
        f"  {'Operation':<20s} {'Duration':>10s} {'Items/s':>10s} {'MB/s':>8s}",
        "  " + "-" * 52,
    ]

    for m in tracker.metrics:
        dur = f"{m.duration:.3f}s" if m.duration < 1 else f"{m.duration:.1f}s"
        lines.append(
            f"  {m.name:<20s} {dur:>10s} {m.items_per_second:>10,.0f} {m.mb_per_second:>8.1f}"
        )

    return "\n".join(lines)
