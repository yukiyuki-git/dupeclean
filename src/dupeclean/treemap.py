"""Enhanced disk usage treemap for DupeClean.

Generates text-based and data-based treemaps showing
how disk space is distributed across directories.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import DirInfo, format_size


@dataclass
class TreemapNode:
    """A node in the treemap."""

    name: str
    path: Path
    size: int
    depth: int
    percentage: float
    is_dir: bool = True
    children: list[TreemapNode] | None = None

    @property
    def size_display(self) -> str:
        return format_size(self.size)


def build_treemap(
    dirs: dict[Path, DirInfo],
    root: Path,
    max_depth: int = 3,
    max_children: int = 10,
) -> TreemapNode:
    """Build a treemap from directory info.

    Args:
        dirs: Directory info map from scanner.
        root: Root directory.
        max_depth: Maximum depth to display.
        max_children: Maximum children per node.

    Returns:
        Root TreemapNode with children.
    """
    root_info = dirs.get(root)
    if not root_info:
        return TreemapNode(
            name=root.name or "/",
            path=root,
            size=0,
            depth=0,
            percentage=100.0,
        )

    node = TreemapNode(
        name=root.name or "/",
        path=root,
        size=root_info.total_size,
        depth=0,
        percentage=100.0,
        children=_build_children(dirs, root_info, 1, max_depth, max_children),
    )
    return node


def _build_children(
    dirs: dict[Path, DirInfo],
    parent: DirInfo,
    depth: int,
    max_depth: int,
    max_children: int,
) -> list[TreemapNode]:
    if depth > max_depth:
        return []

    children: list[TreemapNode] = []
    total = parent.total_size if parent.total_size > 0 else 1

    sorted_children = sorted(parent.children, key=lambda c: c.total_size, reverse=True)

    for child in sorted_children[:max_children]:
        pct = (child.total_size / total * 100) if total else 0
        sub_children = (
            _build_children(dirs, child, depth + 1, max_depth, max_children)
            if depth < max_depth
            else None
        )
        children.append(
            TreemapNode(
                name=child.name,
                path=child.path,
                size=child.total_size,
                depth=depth,
                percentage=pct,
                children=sub_children,
            )
        )

    # Add "(other)" if there are more children
    if len(sorted_children) > max_children:
        other_size = sum(c.total_size for c in sorted_children[max_children:])
        other_pct = (other_size / total * 100) if total else 0
        children.append(
            TreemapNode(
                name=f"({len(sorted_children) - max_children} more)",
                path=parent.path / "(other)",
                size=other_size,
                depth=depth,
                percentage=other_pct,
            )
        )

    return children


def format_treemap(
    node: TreemapNode,
    max_width: int = 50,
    show_bar: bool = True,
) -> str:
    """Format treemap as text.

    Args:
        node: Root treemap node.
        max_width: Maximum bar width in characters.
        show_bar: Show visual bar chart.

    Returns:
        Formatted text representation.
    """
    lines = [
        f"Disk Usage Treemap: {node.name}",
        f"  Total: {node.size_display}",
        "",
    ]
    _format_node(node, lines, max_width, show_bar, indent=1)
    return "\n".join(lines)


def _format_node(
    node: TreemapNode,
    lines: list[str],
    max_width: int,
    show_bar: bool,
    indent: int,
) -> None:
    prefix = "  " * indent
    icon = "📁" if node.is_dir else "📄"

    if show_bar and node.percentage > 0:
        bar_width = max(1, int(node.percentage / 100 * max_width))
        bar = "█" * bar_width + "░" * (max_width - bar_width)
        lines.append(
            f"{prefix}{icon} {node.name:<20s} {bar} "
            f"{node.size_display:>10s} ({node.percentage:5.1f}%)"
        )
    else:
        lines.append(f"{prefix}{icon} {node.name}: {node.size_display} ({node.percentage:.1f}%)")

    if node.children:
        for child in node.children:
            _format_node(child, lines, max_width, show_bar, indent + 1)


def treemap_to_dict(node: TreemapNode) -> dict:
    """Convert treemap to dictionary for JSON export."""
    result = {
        "name": node.name,
        "path": str(node.path),
        "size": node.size,
        "percentage": round(node.percentage, 2),
    }
    if node.children:
        result["children"] = [treemap_to_dict(c) for c in node.children]
    return result
