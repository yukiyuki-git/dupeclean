"""File deduplication cleanup preview module for DupeClean.

Preview cleanup operations before execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class PreviewItem:
    """A previewed cleanup item."""

    path: str
    action: str
    size: int = 0
    reason: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class CleanupPreviewV2:
    """Cleanup preview with detailed items."""

    items: list[PreviewItem] = field(default_factory=list)
    strategy: str = "default"

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def total_savings(self) -> int:
        return sum(i.size for i in self.items)

    @property
    def savings_display(self) -> str:
        return format_size(self.total_savings)

    def add(self, item: PreviewItem) -> None:
        self.items.append(item)

    def render(self) -> str:
        """Render preview as text."""
        if not self.items:
            return "No items to preview."

        lines = [
            f"Cleanup Preview: {self.total_items} items, {self.savings_display} savings",
            f"Strategy: {self.strategy}",
            "",
        ]

        for item in self.items[:20]:
            lines.append(f"  [{item.action}] {item.path} ({item.size_display})")
            if item.reason:
                lines.append(f"    {item.reason}")

        if self.total_items > 20:
            lines.append(f"\n  ... and {self.total_items - 20} more")

        return "\n".join(lines)


def create_preview_v2(
    files: list,
    strategy: str = "default",
) -> CleanupPreviewV2:
    """Create a cleanup preview."""
    preview = CleanupPreviewV2(strategy=strategy)
    return preview
