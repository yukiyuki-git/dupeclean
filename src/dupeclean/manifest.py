"""File manifest module for DupeClean.

Create and manage file manifests — comprehensive catalogs of
all files in a directory tree with metadata.
"""

from __future__ import annotations

import csv
import io
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, ScanStats, format_size


@dataclass
class ManifestEntry:
    """A single entry in a file manifest."""

    path: str
    size: int
    mtime: float
    extension: str
    is_symlink: bool = False

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class FileManifest:
    """A complete file manifest."""

    root: Path
    created_at: float = 0.0
    entries: list[ManifestEntry] = field(default_factory=list)
    stats: ScanStats | None = None

    def __post_init__(self) -> None:
        if self.created_at == 0:
            self.created_at = time.time()

    @property
    def count(self) -> int:
        return len(self.entries)

    @property
    def total_size(self) -> int:
        return sum(e.size for e in self.entries)

    @classmethod
    def from_files(cls, root: Path, files: list[FileInfo]) -> FileManifest:
        """Create manifest from file list."""
        manifest = cls(root=root)
        for fi in files:
            try:
                rel = str(fi.path.relative_to(root))
            except ValueError:
                rel = str(fi.path)
            manifest.entries.append(
                ManifestEntry(
                    path=rel,
                    size=fi.size,
                    mtime=fi.mtime,
                    extension=fi.ext,
                    is_symlink=fi.is_symlink,
                )
            )
        return manifest

    def to_json(self) -> str:
        """Export manifest as JSON."""
        data = {
            "root": str(self.root),
            "created_at": self.created_at,
            "count": self.count,
            "total_size": self.total_size,
            "entries": [
                {
                    "path": e.path,
                    "size": e.size,
                    "mtime": e.mtime,
                    "ext": e.extension,
                }
                for e in self.entries
            ],
        }
        return json.dumps(data, indent=2)

    def to_csv(self) -> str:
        """Export manifest as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["path", "size", "mtime", "extension"])
        for e in self.entries:
            writer.writerow([e.path, e.size, e.mtime, e.extension])
        return output.getvalue()

    def save(self, path: Path, format: str = "json") -> None:
        """Save manifest to file."""
        if format == "json":
            content = self.to_json()
        elif format == "csv":
            content = self.to_csv()
        else:
            raise ValueError(f"Unknown format: {format}")
        path.write_text(content, encoding="utf-8")

    @classmethod
    def load_json(cls, path: Path) -> FileManifest:
        """Load manifest from JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        manifest = cls(
            root=Path(data["root"]),
            created_at=data.get("created_at", 0),
        )
        for entry in data.get("entries", []):
            manifest.entries.append(
                ManifestEntry(
                    path=entry["path"],
                    size=entry["size"],
                    mtime=entry.get("mtime", 0),
                    extension=entry.get("ext", ""),
                )
            )
        return manifest


def compare_manifests(old: FileManifest, new: FileManifest) -> dict:
    """Compare two manifests and return differences."""
    old_map = {e.path: e for e in old.entries}
    new_map = {e.path: e for e in new.entries}

    old_paths = set(old_map.keys())
    new_paths = set(new_map.keys())

    added = [new_map[p] for p in (new_paths - old_paths)]
    removed = [old_map[p] for p in (old_paths - new_paths)]
    modified = []

    for path in old_paths & new_paths:
        old_e = old_map[path]
        new_e = new_map[path]
        if old_e.size != new_e.size or old_e.mtime != new_e.mtime:
            modified.append((old_e, new_e))

    return {
        "added": sorted(added, key=lambda e: e.size, reverse=True),
        "removed": sorted(removed, key=lambda e: e.size, reverse=True),
        "modified": modified,
        "unchanged": len(old_paths & new_paths) - len(modified),
    }


def format_manifest_summary(manifest: FileManifest) -> str:
    """Format manifest summary as text."""
    exts: dict[str, tuple[int, int]] = {}
    for entry in manifest.entries:
        ext = entry.extension or "(none)"
        count, size = exts.get(ext, (0, 0))
        exts[ext] = (count + 1, size + entry.size)

    sorted_exts = sorted(exts.items(), key=lambda x: x[1][1], reverse=True)

    lines = [
        f"File Manifest: {manifest.root}",
        f"  Created: {time.ctime(manifest.created_at)}",
        f"  Files: {manifest.count:,}",
        f"  Total: {format_size(manifest.total_size)}",
        "",
        "  Top types:",
    ]

    for ext, (count, size) in sorted_exts[:10]:
        lines.append(f"    .{ext:<12s} {count:>6,} files  {format_size(size):>10s}")

    return "\n".join(lines)
