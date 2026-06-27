"""Cleanup wizard screen for DupeClean TUI."""

from __future__ import annotations

from textual import on
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from ...analyzer import AnalysisResult
from ...config import Config
from ...models import CleanupAction, format_size

CSS = """
CleanupScreen {
    layout: vertical;
}
#cleanup-header {
    height: 3;
    padding: 1 2;
    background: $primary-darken-2;
    color: $warning;
    text-style: bold;
    dock: top;
}
#cleanup-content {
    height: 1fr;
    overflow-y: auto;
    padding: 1 2;
}
#cleanup-actions {
    height: 5;
    padding: 1 2;
    dock: bottom;
    layout: horizontal;
}
#cleanup-actions Button {
    margin: 0 1;
    min-width: 16;
}
"""


class CleanupScreen(Screen):
    """Interactive cleanup wizard for duplicate files."""

    CSS = CSS

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
    ]

    def __init__(
        self,
        result: AnalysisResult,
        config: Config,
    ) -> None:
        super().__init__()
        self.result = result
        self.config = config
        self._selected_action = CleanupAction.DELETE

    def compose(self) -> None:
        yield Header(show_clock=True)
        yield Static(
            f"🧹 Cleanup Wizard — "
            f"{self.result.stats.duplicate_groups} groups, "
            f"{format_size(self.result.stats.wasted_space)} wasted",
            id="cleanup-header",
        )
        with VerticalScroll(id="cleanup-content"):
            yield from self._build_content()
        with Vertical(id="cleanup-actions"):
            yield Static(
                "  Select action: "
                "[bold]d[/]elete | "
                "[bold]h[/]ardlink | "
                "[bold]r[/]ecycle | "
                "[bold]k[/]eep-newest"
            )
            yield Button(
                "Execute Cleanup (dry run)",
                variant="warning",
                id="execute-btn",
            )
        yield Footer()

    def _build_content(self) -> list[Static]:
        widgets: list[Static] = []

        if not self.result.duplicates:
            widgets.append(Static("\n  🎉 No duplicates to clean up!"))
            return widgets

        stats = self.result.stats
        widgets.append(
            Static(
                f"\n  Found [bold red]{stats.duplicate_groups}[/]"
                f" duplicate groups wasting "
                f"[bold red]{format_size(stats.wasted_space)}[/]"
            )
        )
        widgets.append(
            Static(
                "\n  [bold]Strategy:[/]"
                " Keep the file with the shortest path"
                " (most likely original)\n"
            )
        )
        widgets.append(Static("  Preview of cleanup:"))
        widgets.append(Static("  " + "=" * 60))

        for g in self.result.top_duplicates[:20]:
            keep_file = g.files[0] if g.files else None
            remove_count = g.count - 1
            widgets.append(
                Static(f"\n  [bold]Group #{g.group_id}[/]: {g.count} files x {g.size_display}")
            )
            if keep_file:
                widgets.append(Static(f"    [green]KEEP:[/] {keep_file.path}"))
            widgets.append(
                Static(f"    [red]REMOVE {remove_count} copies:[/] saves {g.wasted_display}")
            )

        return widgets

    @on(Button.Pressed, "#execute-btn")
    def on_execute(self) -> None:
        self.notify(
            "Cleanup wizard coming soon!",
            severity="information",
        )

    def action_back(self) -> None:
        self.app.pop_screen()
