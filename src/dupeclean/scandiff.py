"""Scan diff module for DupeClean.

Compare two scans to detect what changed between them:
- New files
- Deleted files
- Modified files (size or mtime changed)
- Disk space changes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class ScanSnapshot:
    """A point-in-time snapshot of directory contents."""

    root: Path
    timestamp: float
    files: dict[str, FileInfo] = field(default_factory=dict)

    @classmethod
    def from_files(cls, root: Path, files: list[FileInfo], timestamp: float) -> ScanSnapshot:
        """Create a snapshot from a file list."""
        snapshot = cls(root=root, timestamp=timestamp)
        for fi in files:
            try:
                rel = str(fi.path.relative_to(root))
            except ValueError:
                rel = str(fi.path)
            snapshot.files[rel] = fi
        return snapshot

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files.values())

    @property
    def file_count(self) -> int:
        return len(self.files)


@dataclass
class ScanDiff:
    """Difference between two scan snapshots."""

    old: ScanSnapshot
    new: ScanSnapshot
    added: list[FileInfo] = field(default_factory=list)
    removed: list[FileInfo] = field(default_factory=list)
    modified: list[tuple[FileInfo, FileInfo]] = field(default_factory=list)
    unchanged: int = 0

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    @property
    def size_change(self) -> int:
        return self.new.total_size - self.old.total_size

    @property
    def size_change_display(self) -> str:
        change = self.size_change
        if change > 0:
            return f"+{format_size(change)}"
        if change < 0:
            return f"-{format_size(abs(change))}"
        return "0 B"


def diff_scans(old: ScanSnapshot, new: ScanSnapshot) -> ScanDiff:
    """Compare two scan snapshots.

    Returns a ScanDiff describing what changed.
    """
    result = ScanDiff(old=old, new=new)

    old_keys = set(old.files.keys())
    new_keys = set(new.files.keys())

    # Added files (in new but not in old)
    for key in new_keys - old_keys:
        result.added.append(new.files[key])

    # Removed files (in old but not in new)
    for key in old_keys - new_keys:
        result.removed.append(old.files[key])

    # Common files — check for modifications
    for key in old_keys & new_keys:
        old_fi = old.files[key]
        new_fi = new.files[key]
        if old_fi.size != new_fi.size or old_fi.mtime != new_fi.mtime:
            result.modified.append((old_fi, new_fi))
        else:
            result.unchanged += 1

    # Sort results
    result.added.sort(key=lambda f: f.size, reverse=True)
    result.removed.sort(key=lambda f: f.size, reverse=True)
    result.modified.sort(key=lambda t: abs(t[1].size - t[0].size), reverse=True)

    return result


def format_diff(diff: ScanDiff) -> str:
    """Format a scan diff as human-readable text."""
    lines = [
        f"Scan diff: {diff.old.root}",
        f"  Old: {diff.old.file_count:,} files, {format_size(diff.old.total_size)}",
        f"  New: {diff.new.file_count:,} files, {format_size(diff.new.total_size)}",
        f"  Change: {diff.size_change_display}",
        "",
        f"  Added:    {len(diff.added):>6,} files",
        f"  Removed:  {len(diff.removed):>6,} files",
        f"  Modified: {len(diff.modified):>6,} files",
        f"  Unchanged:{diff.unchanged:>6,} files",
    ]

    if diff.added:
        lines.append("\n  Top added:")
        for fi in diff.added[:10]:
            lines.append(f"    + {fi.size_display:>10s}  {fi.path.name}")

    if diff.removed:
        lines.append("\n  Top removed:")
        for fi in diff.removed[:10]:
            lines.append(f"    - {fi.size_display:>10s}  {fi.path.name}")

    if diff.modified:
        lines.append("\n  Top modified:")
        for old_fi, new_fi in diff.modified[:10]:
            delta = new_fi.size - old_fi.size
            sign = "+" if delta >= 0 else ""
            lines.append(
                f"    ~ {new_fi.path.name}: "
                f"{old_fi.size_display} -> {new_fi.size_display} "
                f"({sign}{format_size(abs(delta))})"
            )

    return "\n".join(lines)
