"""Statistics screen for DupeClean TUI."""

from __future__ import annotations

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ...analyzer import AnalysisResult
from ...models import format_duration, format_size

CSS = """
StatsScreen {
    layout: vertical;
}
#stats-header {
    height: 3;
    padding: 1 2;
    background: $primary-darken-2;
    color: $accent;
    text-style: bold;
    dock: top;
}
#stats-content {
    height: 1fr;
    overflow-y: auto;
}
.stat-section {
    color: $accent;
    text-style: bold;
    padding: 1 0 0 0;
    margin: 0 0 1 0;
}
"""


class StatsScreen(Screen):
    """Detailed statistics view."""

    CSS = CSS

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
    ]

    def __init__(self, result: AnalysisResult) -> None:
        super().__init__()
        self.result = result

    def compose(self) -> None:
        yield Header(show_clock=True)
        yield Static(
            f"📊 Statistics — {self.result.root}",
            id="stats-header",
        )
        with VerticalScroll(id="stats-content"):
            yield from self._build_stats()
        yield Footer()

    def _build_stats(self) -> list[Static]:
        s = self.result.stats
        widgets: list[Static] = []

        # General
        widgets.append(Static("\n  General", classes="stat-section"))
        widgets.append(Static(f"  {'Directory:':<20s} {self.result.root}"))
        widgets.append(Static(f"  {'Total Size:':<20s} {format_size(s.total_size)}"))
        widgets.append(Static(f"  {'Total Files:':<20s} {s.total_files:,}"))
        widgets.append(Static(f"  {'Total Dirs:':<20s} {s.total_dirs:,}"))
        widgets.append(Static(f"  {'Scan Duration:':<20s} {format_duration(s.scan_duration)}"))

        # Duplicates
        widgets.append(Static("\n  Duplicates", classes="stat-section"))
        widgets.append(Static(f"  {'Groups Found:':<20s} {s.duplicate_groups:,}"))
        widgets.append(Static(f"  {'Duplicate Files:':<20s} {s.duplicate_files:,}"))
        widgets.append(Static(f"  {'Wasted Space:':<20s} {format_size(s.wasted_space)}"))
        widgets.append(Static(f"  {'Waste %:':<20s} {s.dupe_percentage:.2f}%"))
        widgets.append(Static(f"  {'Unique Files:':<20s} {s.unique_files:,}"))

        # Largest file
        if s.largest_file:
            widgets.append(Static("\n  Largest File", classes="stat-section"))
            widgets.append(Static(f"  {'Path:':<20s} {s.largest_file.path}"))
            widgets.append(Static(f"  {'Size:':<20s} {s.largest_file.size_display}"))

        # Extensions table
        widgets.append(Static("\n  File Types", classes="stat-section"))
        widgets.append(Static(f"  {'Extension':<18s} {'Count':>8s}  {'Size':>10s}  {'%':>6s}"))
        widgets.append(Static("  " + "-" * 50))
        for ext, count, size in self.result.top_extensions:
            pct = (size / s.total_size * 100) if s.total_size else 0
            widgets.append(
                Static(
                    f"  .{ext or '(none)':<17s} {count:>8,}  {format_size(size):>10s}  {pct:5.1f}%"
                )
            )

        return widgets

    def action_back(self) -> None:
        self.app.pop_screen()
