"""Main dashboard screen for DupeClean TUI."""

from __future__ import annotations

from textual import on
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Static

from ...analyzer import AnalysisResult
from ...config import Config
from ...models import format_duration, format_size

CSS = """
MainScreen {
    layout: grid;
    grid-size: 2 1;
    grid-columns: 1fr 2fr;
    grid-rows: 1fr;
}
#left-panel {
    background: $panel;
    border-right: solid $border;
    padding: 0;
    height: 100%;
    overflow-y: auto;
}
#right-panel {
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


class MainScreen(Screen):
    BINDINGS = [
        Binding("d", "show_duplicates", "Duplicates"),
        Binding("b", "show_browse", "Browse"),
        Binding("s", "show_stats", "Stats"),
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self, result: AnalysisResult, config: Config) -> None:
        super().__init__()
        self.result = result
        self.config = config

    def compose(self) -> None:
        with Vertical(id="left-panel"):
            yield Static("📊 DupeClean", classes="nav-section")
            yield Static("📋 Overview", classes="nav-item -active", id="nav-overview")
            yield Static("📦 Largest Files", classes="nav-item", id="nav-largest")
            yield Static("🔄 Duplicates", classes="nav-item", id="nav-duplicates")
            yield Static("📁 File Types", classes="nav-item", id="nav-types")
            yield Static("🗂️ Browse", classes="nav-item", id="nav-browse")
        with VerticalScroll(id="right-panel"):
            yield from self._build_overview()

    def _build_overview(self) -> list[Static]:
        s = self.result.stats
        widgets: list[Static] = []
        widgets.append(Static("📊 Summary", classes="section-title"))
        widgets.append(
            Static(
                f"  Total Size: [bold cyan]{format_size(s.total_size)}[/]    Files: [bold]{s.total_files:,}[/]    Dirs: [bold]{s.total_dirs:,}[/]    Scan: [dim]{format_duration(s.scan_duration)}[/]"
            )
        )
        if self.result.duplicates:
            widgets.append(Static(""))
            widgets.append(Static("🔄 Duplicates", classes="section-title"))
            widgets.append(
                Static(
                    f"  Groups: [bold red]{s.duplicate_groups:,}[/]    Files: [bold red]{s.duplicate_files:,}[/]    Wasted: [bold red]{format_size(s.wasted_space)}[/] ([red]{s.dupe_percentage:.1f}%[/])"
                )
            )
        widgets.append(Static(""))
        widgets.append(Static("📁 Top File Types", classes="section-title"))
        for ext, count, size in self.result.top_extensions[:8]:
            pct = (size / s.total_size * 100) if s.total_size else 0
            bar_len = int(pct / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            widgets.append(
                Static(
                    f"  .{ext or '(none)':<10s} {bar} {format_size(size):>10s} ({count:>6,} files, {pct:5.1f}%)"
                )
            )
        widgets.append(Static(""))
        widgets.append(Static("📦 Largest Files", classes="section-title"))
        for i, fi in enumerate(self.result.largest_files[:8], 1):
            parent = str(fi.path.parent)
            if len(parent) > 50:
                parent = "..." + parent[-47:]
            widgets.append(
                Static(
                    f"  {i:>3}. [bold]{fi.size_display:>10s}[/]  {fi.path.name}  [dim]{parent}[/]"
                )
            )
        return widgets

    def _rebuild_content(self, builder) -> None:
        right = self.query_one("#right-panel")
        right.remove_children()
        for widget in builder():
            right.mount(widget)

    @on(Static.Click, ".nav-item")
    def on_nav_click(self, event: Static.Click) -> None:
        widget = event.control
        view_id = widget.id.replace("nav-", "") if widget.id else ""
        self._switch_view(view_id)

    def _switch_view(self, view_id: str) -> None:
        for nav in self.query(".nav-item"):
            nav.remove_class("-active")
        try:
            active_nav = self.query_one(f"#nav-{view_id}")
            active_nav.add_class("-active")
        except Exception:
            pass
        builders = {
            "overview": self._build_overview,
            "largest": self._build_largest,
            "duplicates": self._build_duplicates,
            "types": self._build_types,
            "browse": self._build_browse,
        }
        builder = builders.get(view_id, self._build_overview)
        self._rebuild_content(builder)

    def _build_largest(self) -> list:
        widgets = []
        widgets.append(Static("📦 Largest Files", classes="section-title"))
        for i, fi in enumerate(self.result.largest_files[:100], 1):
            widgets.append(
                Static(
                    f"  {i:>4}. [bold cyan]{fi.size_display:>10s}[/]  {fi.path.name}  [dim]{fi.path.parent}[/]"
                )
            )
        return widgets

    def _build_duplicates(self) -> list:
        widgets = []
        widgets.append(Static("🔄 Duplicate Files", classes="section-title"))
        if not self.result.duplicates:
            widgets.append(Static("  No duplicates found! 🎉"))
            return widgets
        widgets.append(
            Static(
                f"  {len(self.result.duplicates)} groups, {self.result.stats.duplicate_files} files, {format_size(self.result.stats.wasted_space)} wasted\n"
            )
        )
        for g in self.result.top_duplicates[:50]:
            widgets.append(
                Static(
                    f"  [bold red]Group #{g.group_id}[/]: {g.count} x "
                    f"{g.size_display} = [red]{g.wasted_display} wasted[/]"
                )
            )
            for fi in g.files:
                widgets.append(Static(f"    [dim]└[/] {fi.path}"))
            widgets.append(Static(""))
        return widgets

    def _build_types(self) -> list:
        widgets = []
        s = self.result.stats
        widgets.append(Static("📁 File Type Distribution", classes="section-title"))
        for ext, count, size in self.result.top_extensions[:25]:
            pct = (size / s.total_size * 100) if s.total_size else 0
            bar_len = int(pct / 2.5)
            bar = "█" * bar_len + "░" * (40 - bar_len)
            widgets.append(
                Static(
                    f"  .{ext or '(none)':<12s} {bar} [bold]{format_size(size):>10s}[/] ({count:>6,} files, {pct:5.1f}%)"
                )
            )
        return widgets

    def _build_browse(self) -> list:
        widgets = []
        widgets.append(Static("🗂️ Directory Browser", classes="section-title"))
        root_dir = self.result.dirs.get(self.result.root)
        if not root_dir:
            widgets.append(Static("  No directory data"))
            return widgets
        children = self.result.get_dir_children(self.result.root)
        for child in children[:100]:
            if hasattr(child, "path") and hasattr(child, "children"):
                widgets.append(
                    Static(
                        f"  📁 [bold]{child.name}/[/]  [cyan]{child.size_display}[/]  [dim]{child.file_count} files, {child.dir_count} dirs[/]"
                    )
                )
            else:
                widgets.append(Static(f"  📄 {child.path.name}  [cyan]{child.size_display}[/]"))
        return widgets

    def action_show_duplicates(self) -> None:
        self._switch_view("duplicates")

    def action_show_browse(self) -> None:
        self._switch_view("browse")

    def action_show_stats(self) -> None:
        self._switch_view("types")

    def action_refresh(self) -> None:
        self._switch_view("overview")

    def action_quit(self) -> None:
        self.app.exit()
