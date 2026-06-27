"""File annotation module for DupeClean.

Add notes and metadata to files without modifying them.
Annotations are stored in a sidecar JSON file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ANNOTATIONS_FILE = ".dupeclean_annotations.json"


@dataclass
class FileAnnotation:
    """Annotations for a file."""

    path: str
    note: str = ""
    rating: int = 0  # 0-5 stars
    labels: list[str] = field(default_factory=list)
    custom: dict[str, str] = field(default_factory=dict)


@dataclass
class AnnotationStore:
    """Persistent annotation storage."""

    root: Path
    annotations: dict[str, FileAnnotation] = field(default_factory=dict)

    def get(self, filepath: Path) -> FileAnnotation:
        """Get annotation for a file, creating if needed."""
        rel = str(filepath.relative_to(self.root))
        if rel not in self.annotations:
            self.annotations[rel] = FileAnnotation(path=rel)
        return self.annotations[rel]

    def set_note(self, filepath: Path, note: str) -> None:
        """Set a note on a file."""
        self.get(filepath).note = note

    def set_rating(self, filepath: Path, rating: int) -> None:
        """Set a rating (0-5) on a file."""
        self.get(filepath).rating = max(0, min(5, rating))

    def add_label(self, filepath: Path, label: str) -> None:
        """Add a label to a file."""
        ann = self.get(filepath)
        if label not in ann.labels:
            ann.labels.append(label)

    def set_custom(self, filepath: Path, key: str, value: str) -> None:
        """Set a custom metadata key."""
        self.get(filepath).custom[key] = value

    def find_by_label(self, label: str) -> list[str]:
        """Find files with a given label."""
        return [ann.path for ann in self.annotations.values() if label in ann.labels]

    def find_by_rating(self, min_rating: int = 1) -> list[tuple[str, int]]:
        """Find files with a minimum rating."""
        return [
            (ann.path, ann.rating) for ann in self.annotations.values() if ann.rating >= min_rating
        ]

    def save(self, path: Path | None = None) -> None:
        """Save annotations to file."""
        path = path or self.root / ANNOTATIONS_FILE
        data = {
            "version": 1,
            "root": str(self.root),
            "annotations": {
                k: {
                    "path": v.path,
                    "note": v.note,
                    "rating": v.rating,
                    "labels": v.labels,
                    "custom": v.custom,
                }
                for k, v in self.annotations.items()
            },
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, root: Path) -> AnnotationStore:
        """Load annotations from file."""
        path = root / ANNOTATIONS_FILE
        store = cls(root=root)

        if not path.exists():
            return store

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return store

        for key, entry in data.get("annotations", {}).items():
            store.annotations[key] = FileAnnotation(
                path=entry["path"],
                note=entry.get("note", ""),
                rating=entry.get("rating", 0),
                labels=entry.get("labels", []),
                custom=entry.get("custom", {}),
            )

        return store


def format_annotations(store: AnnotationStore) -> str:
    """Format annotation summary as text."""
    if not store.annotations:
        return "No annotations set."

    annotated = [a for a in store.annotations.values() if a.note or a.rating > 0 or a.labels]

    if not annotated:
        return "No annotations set."

    lines = [f"Annotations ({len(annotated)} files):", ""]

    for ann in annotated[:30]:
        stars = "*" * ann.rating if ann.rating > 0 else ""
        labels = ", ".join(ann.labels) if ann.labels else ""
        lines.append(f"  {ann.path}")
        if stars:
            lines.append(f"    Rating: {stars}")
        if ann.note:
            lines.append(f"    Note: {ann.note}")
        if labels:
            lines.append(f"    Labels: {labels}")

    return "\n".join(lines)
