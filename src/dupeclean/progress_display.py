"""File deduplication progress display for DupeClean.

Rich terminal progress display for dedup operations.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import format_size


@dataclass
class ProgressDisplay:
    """Terminal progress display."""

    total: int = 0
    current: int = 0
    stage: str = ""
    file_name: str = ""
    bytes_processed: int = 0
    start_time: float = 0.0

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return min(100.0, self.current / self.total * 100)

    @property
    def elapsed(self) -> float:
        import time

        if self.start_time == 0:
            return 0.0
        return time.monotonic() - self.start_time

    @property
    def rate(self) -> float:
        if self.elapsed <= 0:
            return 0.0
        return self.current / self.elapsed

    @property
    def eta_seconds(self) -> float | None:
        if self.current <= 0 or self.total <= 0:
            return None
        if self.current >= self.total:
            return 0.0
        rate = self.current / self.elapsed if self.elapsed > 0 else 0
        if rate <= 0:
            return None
        return (self.total - self.current) / rate

    def render(self) -> str:
        """Render progress as terminal string."""

        bar_width = 30
        filled = min(bar_width, int(self.percentage / 100 * bar_width))
        bar = "█" * filled + "░" * (bar_width - filled)

        parts = [f"[{bar}] {self.percentage:5.1f}%"]

        if self.file_name:
            name = self.file_name
            if len(name) > 30:
                name = "..." + name[-27:]
            parts.append(name)

        if self.bytes_processed > 0:
            parts.append(format_size(self.bytes_processed))

        if self.eta_seconds is not None:
            eta = self.eta_seconds
            if eta < 60:
                parts.append(f"ETA {eta:.0f}s")
            else:
                parts.append(f"ETA {eta / 60:.1f}m")

        return " | ".join(parts)


def create_progress(total: int, stage: str = "") -> ProgressDisplay:
    """Create a progress display."""
    import time

    return ProgressDisplay(
        total=total,
        stage=stage,
        start_time=time.monotonic(),
    )
