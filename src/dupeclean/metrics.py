"""File deduplication metrics module for DupeClean.

Track and report dedup operation metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class Metric:
    """A single metric measurement."""
    name: str
    value: float
    unit: str = ""
    timestamp: float = 0.0

    @property
    def display(self) -> str:
        if self.unit == "bytes":
            return format_size(int(self.value))
        if self.unit == "seconds":
            return f"{self.value:.2f}s"
        if self.unit == "percent":
            return f"{self.value:.1f}%"
        return f"{self.value}"


@dataclass
class MetricsCollector:
    """Collect and manage dedup metrics."""
    metrics: list[Metric] = field(default_factory=list)

    def record(
        self, name: str, value: float, unit: str = ""
    ) -> None:
        """Record a metric."""
        import time
        self.metrics.append(
            Metric(
                name=name,
                value=value,
                unit=unit,
                timestamp=time.time(),
            )
        )

    def get(self, name: str) -> Metric | None:
        """Get the most recent metric by name."""
        for m in reversed(self.metrics):
            if m.name == name:
                return m
        return None

    def get_all(self, name: str) -> list[Metric]:
        """Get all metrics by name."""
        return [m for m in self.metrics if m.name == name]

    def summary(self) -> dict:
        """Get metrics summary."""
        names: dict[str, list[float]] = {}
        for m in self.metrics:
            names.setdefault(m.name, []).append(m.value)

        return {
            name: {
                "count": len(values),
                "latest": values[-1],
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
            }
            for name, values in names.items()
        }


def format_metrics(collector: MetricsCollector) -> str:
    """Format metrics as text."""
    if not collector.metrics:
        return "No metrics recorded."

    summary = collector.summary()
    lines = [f"Metrics ({len(summary)} tracked):", ""]

    for name, stats in summary.items():
        m = collector.get(name)
        display = m.display if m else str(stats["latest"])
        lines.append(
            f"  {name}: {display} "
            f"(count={stats['count']}, "
            f"min={stats['min']:.1f}, "
            f"max={stats['max']:.1f})"
        )

    return "\n".join(lines)
