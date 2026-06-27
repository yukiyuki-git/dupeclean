"""Stats screen placeholder."""

from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static


class StatsScreen(Screen):
    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self):
        yield Static("Stats screen")

    def action_back(self):
        self.app.pop_screen()
