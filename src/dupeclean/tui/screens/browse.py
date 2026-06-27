"""Browse screen placeholder."""

from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static


class BrowseScreen(Screen):
    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self):
        yield Static("Browse screen")

    def action_back(self):
        self.app.pop_screen()
