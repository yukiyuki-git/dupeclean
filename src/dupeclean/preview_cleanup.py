"""File deduplication cleanup preview for DupeClean.

Show detailed preview of cleanup operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class PreviewEntry:
    """A single preview entry."""

    action: str
    file: FileInfo
    reason: str = ""
    keeper: FileInfo | None = None

    @property
    def size_display(self) -> str:
        return format_size(self.file.size)


@dataclass
class CleanupPreview:
    """Complete cleanup preview."""

    entries: list[PreviewEntry] = field(default_factory=list)
    strategy: str = "shortest_path"

    @property
    def total_actions(self) -> int:
        return len(self.entries)

    @property
    def total_savings(self) -> int:
        return sum(e.file.size for e in self.entries if e.action == "delete")

    def add(self, entry: PreviewEntry) -> None:
        self.entries.append(entry)

    def render(self) -> str:
        """Render preview as text."""
        if not self.entries:
            return "No cleanup actions to preview."

        lines = [
            f"Cleanup Preview: {self.total_actions} actions, "
            f"{format_size(self.total_savings)} savings",
            f"Strategy: {self.strategy}",
            "",
        ]

        for entry in self.entries[:30]:
            marker = "DEL" if entry.action == "delete" else "LNK"
            lines.append(f"  [{marker}] {entry.file.path.name} ({entry.size_display})")
            if entry.keeper:
                lines.append(f"       -> keep: {entry.keeper.path.name}")

        if self.total_actions > 30:
            lines.append(f"\n  ... and {self.total_actions - 30} more")

        return "\n".join(lines)


def create_preview(
    groups: list[DuplicateGroup],
    strategy: str = "shortest_path",
) -> CleanupPreview:
    """Create a cleanup preview from duplicate groups."""
    preview = CleanupPreview(strategy=strategy)

    for group in groups:
        if len(group.files) < 2:
            continue

        keep_idx = _select_keeper(group, strategy)
        keeper = group.files[keep_idx]

        for i, fi in enumerate(group.files):
            if i == keep_idx:
                continue
            preview.add(
                PreviewEntry(
                    action="delete",
                    file=fi,
                    reason=f"Duplicate of {keeper.path.name}",
                    keeper=keeper,
                )
            )

    return preview


def _select_keeper(group: DuplicateGroup, strategy: str) -> int:
    if strategy == "newest":
        return max(range(group.count), key=lambda i: group.files[i].mtime)
    if strategy == "oldest":
        return min(range(group.count), key=lambda i: group.files[i].mtime)
    return min(range(group.count), key=lambda i: len(str(group.files[i].path)))
