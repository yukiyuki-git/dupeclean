"""Directory browser screen for DupeClean TUI."""

from __future__ import annotations

import contextlib
from pathlib import Path

from textual import on
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ...analyzer import AnalysisResult
from ...models import DirInfo, FileInfo

CSS = """
BrowseScreen {
    layout: vertical;
}
#browse-path {
    height: 3;
    padding: 1 2;
    background: $primary-darken-2;
    color: $accent;
    text-style: bold;
    dock: top;
}
#browse-content {
    height: 1fr;
    overflow-y: auto;
}
.browse-item {
    height: 1;
    padding: 0 2;
}
.browse-item:hover {
    background: $primary-darken-3;
}
.dir-item {
    text-style: bold;
}
"""


class BrowseScreen(Screen):
    """Interactive directory browser with navigation."""

    CSS = CSS

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "select", "Open"),
        Binding("backspace", "up", "Up"),
    ]

    def __init__(
        self,
        result: AnalysisResult,
        start_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.result = result
        self.current_path = start_path or result.root
        self._history: list[Path] = []

    def compose(self) -> None:
        yield Header(show_clock=True)
        yield Static(
            f"📂 {self.current_path}",
            id="browse-path",
        )
        with VerticalScroll(id="browse-content"):
            yield from self._build_listing()
        yield Footer()

    def _build_listing(self) -> list[Static]:
        children = self.result.get_dir_children(self.current_path)
        widgets: list[Static] = []

        if not children:
            widgets.append(Static("  (empty directory)"))
            return widgets

        for child in children:
            if isinstance(child, DirInfo):
                widgets.append(
                    Static(
                        f"  📁 [bold]{child.name}/[/]  "
                        f"[cyan]{child.size_display}[/]  "
                        f"[dim]{child.file_count} files[/]",
                        id=f"dir:{child.path}",
                        classes="browse-item dir-item",
                    )
                )
            elif isinstance(child, FileInfo):
                widgets.append(
                    Static(
                        f"  📄 {child.path.name}  "
                        f"[cyan]{child.size_display}[/]  "
                        f"[dim]{child.ext or '-'}[/]",
                        id=f"file:{child.path}",
                        classes="browse-item file-item",
                    )
                )
        return widgets

    def _navigate(self, path: Path) -> None:
        if path in self.result.dirs:
            self._history.append(self.current_path)
            self.current_path = path
            self._refresh()

    def _go_up(self) -> None:
        if self._history:
            self.current_path = self._history.pop()
        elif self.current_path != self.result.root:
            self.current_path = self.current_path.parent
        self._refresh()

    def _refresh(self) -> None:
        with contextlib.suppress(Exception):
            self.query_one("#browse-path").update(f"📂 {self.current_path}")
        content = self.query_one("#browse-content")
        content.remove_children()
        for widget in self._build_listing():
            content.mount(widget)

    @on(Static.Click, ".dir-item")
    def on_dir_click(self, event: Static.Click) -> None:
        widget = event.control
        if widget.id and widget.id.startswith("dir:"):
            path = Path(widget.id[4:])
            self._navigate(path)

    def action_select(self) -> None:
        focused = self.focused
        if focused and focused.id and focused.id.startswith("dir:"):
            path = Path(focused.id[4:])
            self._navigate(path)

    def action_up(self) -> None:
        self._go_up()

    def action_back(self) -> None:
        self.app.pop_screen()
