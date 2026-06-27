"""Treemap screen placeholder."""

from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static


class TreemapScreen(Screen):
    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self):
        yield Static("Treemap screen")

    def action_back(self):
        self.app.pop_screen()
