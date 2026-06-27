"""CLI progress bar with ETA for DupeClean.

Provides a rich progress bar for terminal operations
with estimated time remaining, speed display, and
animated spinner.
"""

from __future__ import annotations

import sys
import time
from typing import TextIO


class ProgressBar:
    """Terminal progress bar with ETA.

    Displays: [████████░░░░░░░░] 50.0% (500/1000) ETA: 2.3s
    """

    def __init__(
        self,
        total: int = 100,
        width: int = 30,
        stream: TextIO | None = None,
        show_speed: bool = True,
    ) -> None:
        self.total = total
        self.width = width
        self.stream = stream or sys.stderr
        self.show_speed = show_speed
        self.current = 0
        self.message = ""
        self._start_time = time.monotonic()
        self._last_update = 0.0
        self._min_interval = 0.05  # 50ms between updates

    def update(self, increment: int = 1, message: str = "") -> None:
        """Update progress."""
        self.current += increment
        if message:
            self.message = message
        self._render()

    def set(self, value: int, message: str = "") -> None:
        """Set absolute progress value."""
        self.current = value
        if message:
            self.message = message
        self._render()

    def _render(self) -> None:
        """Render the progress bar."""
        now = time.monotonic()
        if now - self._last_update < self._min_interval:
            return
        self._last_update = now

        if self.total > 0:
            pct = min(100.0, self.current / self.total * 100)
            filled = int(self.current / self.total * self.width)
        else:
            pct = 0.0
            filled = 0

        empty = self.width - filled
        bar = "█" * filled + "░" * empty

        elapsed = now - self._start_time
        eta_str = self._format_eta(elapsed)

        parts = [f"\r  [{bar}] {pct:5.1f}%"]
        parts.append(f" ({self.current:,}/{self.total:,})")

        if eta_str:
            parts.append(f" ETA: {eta_str}")

        if self.show_speed and elapsed > 0:
            speed = self.current / elapsed
            if speed > 1:
                parts.append(f" ({speed:.0f}/s)")

        if self.message:
            msg = self.message
            if len(msg) > 30:
                msg = msg[:27] + "..."
            parts.append(f" {msg}")

        line = "".join(parts)
        self.stream.write(line)
        self.stream.write(" \r")
        self.stream.flush()

    def _format_eta(self, elapsed: float) -> str:
        """Format estimated time remaining."""
        if self.current <= 0 or self.total <= 0:
            return ""
        if self.current >= self.total:
            return "done"
        if elapsed <= 0:
            return ""

        rate = self.current / elapsed
        if rate <= 0:
            return ""

        remaining = (self.total - self.current) / rate

        if remaining < 1:
            return "<1s"
        if remaining < 60:
            return f"{remaining:.0f}s"
        if remaining < 3600:
            minutes = int(remaining // 60)
            secs = int(remaining % 60)
            return f"{minutes}m {secs}s"
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return f"{hours}h {minutes}m"

    def finish(self, message: str = "Done") -> None:
        """Finish the progress bar."""
        self.current = self.total
        elapsed = time.monotonic() - self._start_time
        self.stream.write(
            f"\r  [{'█' * self.width}] 100.0% "
            f"({self.total:,}/{self.total:,}) "
            f"in {elapsed:.1f}s — {message}"
            f"{' ' * 20}\n"
        )
        self.stream.flush()

    def __enter__(self) -> ProgressBar:
        return self

    def __exit__(self, *args) -> None:
        self.finish()


class Spinner:
    """Animated terminal spinner for indeterminate progress."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(
        self,
        message: str = "Working...",
        stream: TextIO | None = None,
    ) -> None:
        self.message = message
        self.stream = stream or sys.stderr
        self._frame = 0
        self._running = False

    def spin(self) -> None:
        """Advance one frame."""
        char = self.FRAMES[self._frame % len(self.FRAMES)]
        self.stream.write(f"\r  {char} {self.message}  ")
        self.stream.flush()
        self._frame += 1

    def update(self, message: str) -> None:
        """Update spinner message."""
        self.message = message
        self.spin()

    def stop(self, message: str = "Done") -> None:
        """Stop the spinner."""
        self.stream.write(f"\r  ✓ {message}{' ' * 20}\n")
        self.stream.flush()
