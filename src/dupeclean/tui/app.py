"""Main Textual application for DupeClean."""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Footer, Header, Static

from ..analyzer import AnalysisResult, Analyzer
from ..config import Config

CSS = """
Screen {
    background: $surface;
}
#main-layout {
    height: 100%;
}
#left-panel {
    width: 30;
    background: $panel;
    border-right: solid $border;
    padding: 0;
    height: 100%;
    overflow-y: auto;
}
#right-panel {
    width: 1fr;
    height: 100%;
    overflow-y: auto;
}
.nav-section {
    padding: 1 2;
    background: $primary-darken-3;
    color: $accent;
    text-style: bold;
    dock: top;
    height: 3;
}
.nav-item {
    height: 3;
    padding: 1 2;
    background: $panel;
}
.nav-item:hover {
    background: $primary-darken-2;
}
.nav-item.-active {
    background: $primary-darken-1;
    border-left: thick $accent;
}
.section-title {
    color: $accent;
    text-style: bold;
    padding: 1 0 0 0;
    margin: 0 0 1 0;
}
"""


class DupeCleanApp(App):
    TITLE = "🔍 DupeClean"
    SUB_TITLE = "Smart Disk Analyzer"
    CSS = CSS

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("question_mark", "help", "Help", show=True, key_display="?"),
    ]

    def __init__(self, target: Path, config: Config | None = None) -> None:
        super().__init__()
        self.target = target
        self.config = config or Config()
        self.result: AnalysisResult | None = None
        self._scanning = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-layout"):
            with Vertical(id="left-panel"):
                yield Static("📊 DupeClean", classes="nav-section")
            with Vertical(id="right-panel"):
                yield Static(f"📂 Scanning: {self.target}", id="welcome-msg")
        yield Footer()

    def on_mount(self) -> None:
        self._start_scan()

    @work(exclusive=True, group="scan")
    async def _start_scan(self) -> None:
        self._scanning = True
        self.notify("Starting scan...", severity="information")
        try:
            analyzer = Analyzer(self.config)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, analyzer.analyze, self.target)
            self.result = result
            self._scanning = False
            self._show_results()
        except Exception as e:
            self._scanning = False
            self.notify(f"Scan failed: {e}", severity="error")

    def _show_results(self) -> None:
        if not self.result:
            return
        from .screens.main import MainScreen

        with contextlib.suppress(NoMatches):
            self.pop_screen()
        self.push_screen(MainScreen(self.result, self.config))

    def action_help(self) -> None:
        from .screens.help import HelpScreen

        self.push_screen(HelpScreen())

    def action_quit(self) -> None:
        self.exit()
