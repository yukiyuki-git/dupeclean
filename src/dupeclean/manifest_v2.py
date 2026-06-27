"""File deduplication manifest for DupeClean.

Create manifests of dedup operations for audit trails.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size


@dataclass
class ManifestEntry:
    """A single manifest entry."""

    path: str
    action: str  # "kept", "removed", "hardlinked"
    size: int = 0
    hash_value: str = ""
    reason: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class DedupManifest:
    """A manifest of a dedup operation."""

    operation_id: str
    timestamp: float
    root: str
    entries: list[ManifestEntry] = field(default_factory=list)

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    @property
    def kept_count(self) -> int:
        return sum(1 for e in self.entries if e.action == "kept")

    @property
    def removed_count(self) -> int:
        return sum(1 for e in self.entries if e.action in ("removed", "hardlinked"))

    def add_entry(self, entry: ManifestEntry) -> None:
        self.entries.append(entry)

    def save(self, path: Path) -> None:
        data = {
            "operation_id": self.operation_id,
            "timestamp": self.timestamp,
            "root": self.root,
            "entries": [
                {
                    "path": e.path,
                    "action": e.action,
                    "size": e.size,
                    "hash": e.hash_value,
                    "reason": e.reason,
                }
                for e in self.entries
            ],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> DedupManifest | None:
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            manifest = cls(
                operation_id=data["operation_id"],
                timestamp=data["timestamp"],
                root=data["root"],
            )
            for entry in data.get("entries", []):
                manifest.entries.append(
                    ManifestEntry(
                        path=entry["path"],
                        action=entry["action"],
                        size=entry.get("size", 0),
                        hash_value=entry.get("hash", ""),
                        reason=entry.get("reason", ""),
                    )
                )
            return manifest
        except (json.JSONDecodeError, OSError, KeyError):
            return None


def format_manifest(manifest: DedupManifest) -> str:
    """Format manifest as text."""
    import datetime

    dt = datetime.datetime.fromtimestamp(manifest.timestamp)
    lines = [
        f"Dedup Manifest: {manifest.operation_id}",
        f"  Root: {manifest.root}",
        f"  Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}",
        f"  Entries: {manifest.total_entries:,}",
        f"  Kept: {manifest.kept_count:,}",
        f"  Removed: {manifest.removed_count:,}",
    ]

    # Show some entries
    removed = [e for e in manifest.entries if e.action in ("removed", "hardlinked")]
    if removed:
        lines.append("\n  Removed files:")
        for e in removed[:10]:
            lines.append(f"    {e.action}: {e.path} ({e.size_display})")

    return "\n".join(lines)
