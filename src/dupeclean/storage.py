"""File deduplication storage manager for DupeClean.

Manage deduplicated file storage with content-defined chunking.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class StorageEntry:
    """An entry in dedup storage."""

    content_hash: str
    size: int
    ref_count: int = 1
    original_path: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class StorageManager:
    """Manage deduplicated file storage."""

    entries: dict[str, StorageEntry] = field(default_factory=dict)

    def add_reference(self, content_hash: str, size: int, path: str = "") -> None:
        """Add a reference to content."""
        if content_hash in self.entries:
            self.entries[content_hash].ref_count += 1
        else:
            self.entries[content_hash] = StorageEntry(
                content_hash=content_hash,
                size=size,
                original_path=path,
            )

    def remove_reference(self, content_hash: str) -> bool:
        """Remove a reference. Returns True if entry removed."""
        if content_hash not in self.entries:
            return False
        self.entries[content_hash].ref_count -= 1
        if self.entries[content_hash].ref_count <= 0:
            del self.entries[content_hash]
            return True
        return False

    def get_entry(self, content_hash: str) -> StorageEntry | None:
        """Get storage entry by hash."""
        return self.entries.get(content_hash)

    def get_duplicated(self) -> list[StorageEntry]:
        """Get entries with multiple references."""
        return [e for e in self.entries.values() if e.ref_count > 1]

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    @property
    def total_references(self) -> int:
        return sum(e.ref_count for e in self.entries.values())

    @property
    def unique_size(self) -> int:
        return sum(e.size for e in self.entries.values())

    @property
    def deduplicated_size(self) -> int:
        """Size if all duplicates were removed."""
        return sum(e.size for e in self.entries.values())

    @property
    def wasted_size(self) -> int:
        """Space wasted by duplicates."""
        return sum(e.size * (e.ref_count - 1) for e in self.entries.values() if e.ref_count > 1)

    def stats(self) -> dict:
        """Get storage statistics."""
        dupes = self.get_duplicated()
        return {
            "total_entries": self.total_entries,
            "total_references": self.total_references,
            "unique_size": self.unique_size,
            "wasted_size": self.wasted_size,
            "duplicate_entries": len(dupes),
            "dedup_ratio": (
                1 - (self.total_entries / self.total_references) if self.total_references > 0 else 0
            ),
        }


def format_storage_stats(manager: StorageManager) -> str:
    """Format storage stats as text."""
    s = manager.stats()
    lines = [
        "Storage Statistics:",
        f"  Entries: {s['total_entries']:,}",
        f"  References: {s['total_references']:,}",
        f"  Unique size: {format_size(s['unique_size'])}",
        f"  Wasted: {format_size(s['wasted_size'])}",
        f"  Dedup ratio: {s['dedup_ratio']:.1%}",
        f"  Duplicate entries: {s['duplicate_entries']:,}",
    ]
    return "\n".join(lines)
