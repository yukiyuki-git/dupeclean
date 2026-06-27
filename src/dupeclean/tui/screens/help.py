"""Help screen for DupeClean TUI."""

from __future__ import annotations

from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Static


HELP_TEXT = """
[bold cyan]🔍 DupeClean[/] — Smart Disk Analyzer & Duplicate Finder

[bold]Navigation[/]
  ↑/↓ or j/k    Navigate items
  Enter          Open directory / Select item
  Backspace      Go up / Go back

[bold]Views[/]
  d              Show duplicates view
  b              Browse directories
  s              Show statistics
  r              Refresh / Overview

[bold]General[/]
  q / Esc        Quit / Go back
  ?              Show this help

[bold]Tips[/]
  • Duplicates are sorted by wasted space (biggest waste first)
  • Files are hashed in 3 stages for speed: quick → medium → full
  • Use --cli flag for non-interactive mode
  • Use --report html to generate a shareable report
"""


class HelpScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("q", "back", "Back"),
        Binding("question_mark", "back", "Back"),
    ]

    def compose(self) -> None:
        with VerticalScroll():
            yield Static(HELP_TEXT, id="help-text")

    def action_back(self) -> None:
        self.app.pop_screen()
