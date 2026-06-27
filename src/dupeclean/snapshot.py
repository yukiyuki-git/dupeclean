"""File snapshot module for DupeClean.

Create point-in-time snapshots of directory state for
change tracking and rollback.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class Snapshot:
    """A point-in-time snapshot of directory contents."""

    name: str
    root: Path
    timestamp: float
    files: dict[str, int] = field(default_factory=dict)  # path -> size
    file_hashes: dict[str, str] = field(default_factory=dict)  # path -> hash

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(self.files.values())


@dataclass
class SnapshotDiff:
    """Difference between two snapshots."""

    old_name: str
    new_name: str
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    unchanged: int = 0

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)


def create_snapshot(name: str, root: Path, files: list[FileInfo]) -> Snapshot:
    """Create a snapshot from file list."""
    snapshot = Snapshot(
        name=name,
        root=root,
        timestamp=time.time(),
    )
    for fi in files:
        try:
            rel = str(fi.path.relative_to(root))
        except ValueError:
            rel = str(fi.path)
        snapshot.files[rel] = fi.size
        if fi.hash_for_dedup:
            snapshot.file_hashes[rel] = fi.hash_for_dedup
    return snapshot


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Compare two snapshots."""
    old_paths = set(old.files.keys())
    new_paths = set(new.files.keys())

    diff = SnapshotDiff(
        old_name=old.name,
        new_name=new.name,
    )

    diff.added = sorted(new_paths - old_paths)
    diff.removed = sorted(old_paths - new_paths)

    for path in old_paths & new_paths:
        old_size = old.files[path]
        new_size = new.files[path]
        old_hash = old.file_hashes.get(path)
        new_hash = new.file_hashes.get(path)

        if old_size != new_size or (old_hash and new_hash and old_hash != new_hash):
            diff.modified.append(path)
        else:
            diff.unchanged += 1

    return diff


def save_snapshot(snapshot: Snapshot, path: Path) -> None:
    """Save snapshot to JSON file."""
    data = {
        "name": snapshot.name,
        "root": str(snapshot.root),
        "timestamp": snapshot.timestamp,
        "files": snapshot.files,
        "hashes": snapshot.file_hashes,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_snapshot(path: Path) -> Snapshot | None:
    """Load snapshot from JSON file."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Snapshot(
            name=data["name"],
            root=Path(data["root"]),
            timestamp=data["timestamp"],
            files=data.get("files", {}),
            file_hashes=data.get("hashes", {}),
        )
    except (json.JSONDecodeError, OSError, KeyError):
        return None


def format_snapshot(snapshot: Snapshot) -> str:
    """Format snapshot as text."""
    import datetime

    dt = datetime.datetime.fromtimestamp(snapshot.timestamp)
    return (
        f"Snapshot: {snapshot.name}\n"
        f"  Root: {snapshot.root}\n"
        f"  Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"  Files: {snapshot.file_count:,}\n"
        f"  Size: {format_size(snapshot.total_size)}"
    )


def format_snapshot_diff(diff: SnapshotDiff) -> str:
    """Format snapshot diff as text."""
    lines = [
        f"Diff: {diff.old_name} -> {diff.new_name}",
        f"  Added: {len(diff.added):,}",
        f"  Removed: {len(diff.removed):,}",
        f"  Modified: {len(diff.modified):,}",
        f"  Unchanged: {diff.unchanged:,}",
    ]

    if diff.added:
        lines.append("\n  Added files:")
        for p in diff.added[:10]:
            lines.append(f"    + {p}")

    if diff.removed:
        lines.append("\n  Removed files:")
        for p in diff.removed[:10]:
            lines.append(f"    - {p}")

    if diff.modified:
        lines.append("\n  Modified files:")
        for p in diff.modified[:10]:
            lines.append(f"    ~ {p}")

    return "\n".join(lines)
