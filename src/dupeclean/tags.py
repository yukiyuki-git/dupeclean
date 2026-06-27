"""File tagging module for DupeClean.

Tag files with labels for organization without moving them.
Tags are stored in a sidecar JSON file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

TAG_FILE = ".dupeclean_tags.json"


@dataclass
class FileTag:
    """A tag on a file."""

    path: str  # Relative path
    tags: list[str] = field(default_factory=list)
    note: str = ""


@dataclass
class TagStore:
    """Persistent tag storage."""

    root: Path
    tags: dict[str, FileTag] = field(default_factory=dict)

    def add_tag(self, filepath: Path, tag: str) -> None:
        """Add a tag to a file."""
        rel = str(filepath.relative_to(self.root))
        if rel not in self.tags:
            self.tags[rel] = FileTag(path=rel)
        if tag not in self.tags[rel].tags:
            self.tags[rel].tags.append(tag)

    def remove_tag(self, filepath: Path, tag: str) -> bool:
        """Remove a tag from a file."""
        rel = str(filepath.relative_to(self.root))
        if rel in self.tags and tag in self.tags[rel].tags:
            self.tags[rel].tags.remove(tag)
            return True
        return False

    def get_tags(self, filepath: Path) -> list[str]:
        """Get tags for a file."""
        rel = str(filepath.relative_to(self.root))
        if rel in self.tags:
            return list(self.tags[rel].tags)
        return []

    def set_note(self, filepath: Path, note: str) -> None:
        """Set a note on a file."""
        rel = str(filepath.relative_to(self.root))
        if rel not in self.tags:
            self.tags[rel] = FileTag(path=rel)
        self.tags[rel].note = note

    def find_by_tag(self, tag: str) -> list[str]:
        """Find all files with a given tag."""
        return [ft.path for ft in self.tags.values() if tag in ft.tags]

    def all_tags(self) -> list[str]:
        """Get all unique tags."""
        tags: set[str] = set()
        for ft in self.tags.values():
            tags.update(ft.tags)
        return sorted(tags)

    def save(self, path: Path | None = None) -> None:
        """Save tags to file."""
        path = path or self.root / TAG_FILE
        data = {
            "version": 1,
            "root": str(self.root),
            "tags": {
                k: {"path": v.path, "tags": v.tags, "note": v.note} for k, v in self.tags.items()
            },
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, root: Path) -> TagStore:
        """Load tags from file."""
        path = root / TAG_FILE
        store = cls(root=root)

        if not path.exists():
            return store

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return store

        for key, entry in data.get("tags", {}).items():
            store.tags[key] = FileTag(
                path=entry["path"],
                tags=entry.get("tags", []),
                note=entry.get("note", ""),
            )

        return store


def format_tag_summary(store: TagStore) -> str:
    """Format tag summary as text."""
    all_tags = store.all_tags()
    if not all_tags:
        return "No tags set."

    lines = [f"Tags ({len(all_tags)} unique, {len(store.tags)} files):", ""]

    for tag in all_tags:
        files = store.find_by_tag(tag)
        lines.append(f"  [{tag}] ({len(files)} files)")
        for f in files[:5]:
            lines.append(f"    {f}")
        if len(files) > 5:
            lines.append(f"    ... and {len(files) - 5} more")

    return "\n".join(lines)
