"""Treemap visualization screen for DupeClean TUI."""

from __future__ import annotations

from pathlib import Path

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ...analyzer import AnalysisResult
from ...models import format_size

# Color palette for treemap bars
COLORS = [
    "#7aa2f7",
    "#bb9af7",
    "#7dcfff",
    "#73daca",
    "#9ece6a",
    "#e0af68",
    "#f7768e",
    "#ff9e64",
    "#2ac3de",
    "#b4f9f8",
    "#cfc9c2",
    "#565f89",
]


class TreemapScreen(Screen):
    """Text-based treemap visualization of disk usage."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        result: AnalysisResult,
        path: Path | None = None,
    ) -> None:
        super().__init__()
        self.result = result
        self.target = path or result.root

    def compose(self) -> None:
        yield Header(show_clock=True)
        yield Static(
            f"📊 Treemap: {self.target}",
            id="treemap-title",
            classes="section-title",
        )
        with VerticalScroll(id="treemap-content"):
            yield from self._render_treemap()
        yield Static(
            "  [dim]Each block represents proportional disk usage. Press ESC to go back.[/]",
            id="treemap-help",
        )
        yield Footer()

    def _render_treemap(self) -> list[Static]:
        dir_info = self.result.dirs.get(self.target)
        if not dir_info:
            return [Static("  No data available")]

        children_data: list[tuple[str, int]] = []
        for child in dir_info.children[:12]:
            children_data.append((child.name, child.total_size))

        if dir_info.files:
            other_size = sum(f.size for f in dir_info.files)
            if other_size > 0:
                children_data.append(("(files)", other_size))

        if not children_data:
            return [Static("  No children")]

        children_data.sort(key=lambda x: x[1], reverse=True)
        total_size = sum(size for _, size in children_data)

        widgets: list[Static] = []
        widgets.append(Static(f"  Total: {format_size(total_size)}"))
        widgets.append(Static(""))

        width = 50
        for i, (name, size) in enumerate(children_data):
            pct = (size / total_size * 100) if total_size > 0 else 0
            bar_width = max(1, int(pct / 100 * width))
            bar = "█" * bar_width + "░" * (width - bar_width)
            color = COLORS[i % len(COLORS)]

            widgets.append(
                Static(
                    f"  [on {color}] [/] {bar} "
                    f"[bold]{format_size(size):>10s}[/] "
                    f"({pct:5.1f}%)  {name}"
                )
            )

        return widgets

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_quit(self) -> None:
        self.app.exit()
