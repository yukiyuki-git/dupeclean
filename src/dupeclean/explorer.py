"""File deduplication file explorer for DupeClean.

Explore and navigate file systems with dedup awareness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size


@dataclass
class ExplorerNode:
    """A node in the file explorer."""

    name: str
    path: Path
    is_dir: bool
    size: int = 0
    children: list[ExplorerNode] = field(default_factory=list)
    depth: int = 0

    @property
    def size_display(self) -> str:
        return format_size(self.size)

    @property
    def icon(self) -> str:
        return "📁" if self.is_dir else "📄"


class FileExplorer:
    """File system explorer with dedup awareness."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.current = root
        self._history: list[Path] = []

    def navigate(self, path: Path) -> None:
        """Navigate to a directory."""
        if path.is_dir():
            self._history.append(self.current)
            self.current = path

    def go_up(self) -> None:
        """Go to parent directory."""
        if self._history:
            self.current = self._history.pop()
        elif self.current != self.root:
            self.current = self.current.parent

    def get_children(self) -> list[ExplorerNode]:
        """Get children of current directory."""
        children: list[ExplorerNode] = []
        try:
            for item in sorted(self.current.iterdir()):
                try:
                    is_dir = item.is_dir()
                    size = 0 if is_dir else item.stat().st_size
                    children.append(
                        ExplorerNode(
                            name=item.name,
                            path=item,
                            is_dir=is_dir,
                            size=size,
                        )
                    )
                except (OSError, PermissionError):
                    continue
        except (OSError, PermissionError):
            pass
        return children

    def render(self) -> str:
        """Render current directory as text."""
        children = self.get_children()
        lines = [
            f"📂 {self.current}",
            f"  {len(children)} items",
            "",
        ]

        for child in children[:50]:
            icon = child.icon
            lines.append(f"  {icon} {child.name:<30s} {child.size_display:>10s}")

        return "\n".join(lines)
