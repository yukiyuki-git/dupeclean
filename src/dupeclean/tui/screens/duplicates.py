"""Duplicate groups screen for DupeClean TUI."""

from __future__ import annotations

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ...analyzer import AnalysisResult
from ...config import Config
from ...models import format_size

CSS = """
DuplicateScreen {
    layout: vertical;
}
#dup-summary {
    height: 3;
    padding: 1 2;
    background: $primary-darken-2;
    color: $error;
    text-style: bold;
    dock: top;
}
#dup-content {
    height: 1fr;
    overflow-y: auto;
}
.dup-header {
    color: $error;
    text-style: bold;
    margin: 1 0 0 0;
}
.dup-file {
    padding: 0 0 0 4;
    color: $text;
}
.dup-file:hover {
    background: $primary-darken-3;
}
"""


class DuplicateScreen(Screen):
    """Screen showing all duplicate file groups."""

    CSS = CSS

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
    ]

    def __init__(self, result: AnalysisResult, config: Config) -> None:
        super().__init__()
        self.result = result
        self.config = config

    def compose(self) -> None:
        yield Header(show_clock=True)
        yield Static(
            f"🔄 {self.result.stats.duplicate_groups} groups | "
            f"{self.result.stats.duplicate_files} files | "
            f"{format_size(self.result.stats.wasted_space)} wasted",
            id="dup-summary",
        )
        with VerticalScroll(id="dup-content"):
            yield from self._build_groups()
        yield Footer()

    def _build_groups(self) -> list[Static]:
        widgets: list[Static] = []

        if not self.result.duplicates:
            widgets.append(Static("\n  🎉 No duplicates found!"))
            return widgets

        widgets.append(
            Static(
                "\n  Duplicate files sorted by wasted space\n"
                "  [bold green]★ KEEP[/] = shortest path "
                "(suggested keep)\n"
            )
        )

        for group in self.result.top_duplicates[:100]:
            widgets.append(
                Static(
                    f"\n  Group #{group.group_id}: "
                    f"{group.count} files x "
                    f"{group.size_display} = "
                    f"[bold red]{group.wasted_display} wasted[/]",
                    classes="dup-header",
                )
            )
            for i, fi in enumerate(group.files):
                marker = "[bold green]★ KEEP[/]" if i == 0 else "[red]✕[/]"
                widgets.append(
                    Static(
                        f"    {marker} {fi.path}  [dim]({fi.size_display})[/]",
                        classes="dup-file",
                    )
                )
        return widgets

    def action_back(self) -> None:
        self.app.pop_screen()
