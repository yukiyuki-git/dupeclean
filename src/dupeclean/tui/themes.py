"""Color themes for DupeClean TUI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Theme:
    name: str
    accent: str = "#7aa2f7"
    danger: str = "#f7768e"
    success: str = "#9ece6a"
    warning: str = "#e0af68"
    muted: str = "#565f89"
    surface: str = "#24283b"
    background: str = "#1a1b26"
    foreground: str = "#c0caf5"
    border: str = "#292e42"


THEMES: dict[str, Theme] = {
    "default": Theme(name="Tokyo Night"),
    "dark": Theme(
        name="Dark",
        accent="#61afef",
        danger="#e06c75",
        success="#98c379",
        warning="#d19a66",
        muted="#5c6370",
        surface="#282c34",
        background="#282c34",
        foreground="#abb2bf",
        border="#3e4452",
    ),
    "monokai": Theme(
        name="Monokai",
        accent="#66d9ef",
        danger="#f92672",
        success="#a6e22e",
        warning="#e6db74",
        muted="#75715e",
        surface="#272822",
        background="#272822",
        foreground="#f8f8f2",
        border="#3e3d32",
    ),
    "dracula": Theme(
        name="Dracula",
        accent="#bd93f9",
        danger="#ff5555",
        success="#50fa7b",
        warning="#f1fa8c",
        muted="#6272a4",
        surface="#282a36",
        background="#282a36",
        foreground="#f8f8f2",
        border="#44475a",
    ),
}


def get_theme(name: str) -> Theme:
    return THEMES.get(name, THEMES["default"])
