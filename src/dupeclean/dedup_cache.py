"""File deduplication cache module for DupeClean.

Cache dedup results for faster subsequent scans.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo


@dataclass
class CacheEntry:
    """A cached dedup result entry."""

    path: str
    size: int
    mtime: float
    hash_value: str
    group_id: int = -1


@dataclass
class DedupCache:
    """Cache for dedup results."""

    entries: dict[str, CacheEntry] = field(default_factory=dict)
    last_updated: float = 0.0

    def add(self, fi: FileInfo, hash_val: str, group_id: int = -1) -> None:
        """Add a file to cache."""
        key = str(fi.path)
        self.entries[key] = CacheEntry(
            path=key,
            size=fi.size,
            mtime=fi.mtime,
            hash_value=hash_val,
            group_id=group_id,
        )

    def get(self, path: Path) -> CacheEntry | None:
        """Get cached entry for a path."""
        return self.entries.get(str(path))

    def is_valid(self, fi: FileInfo) -> bool:
        """Check if cached entry is still valid."""
        entry = self.get(fi.path)
        if entry is None:
            return False
        return entry.size == fi.size and entry.mtime == fi.mtime

    def get_hash(self, fi: FileInfo) -> str | None:
        """Get cached hash if valid."""
        if self.is_valid(fi):
            entry = self.get(fi.path)
            if entry:
                return entry.hash_value
        return None

    def save(self, path: Path) -> None:
        """Save cache to file."""
        self.last_updated = time.time()
        data = {
            "version": 1,
            "updated": self.last_updated,
            "entries": {
                k: {
                    "path": v.path,
                    "size": v.size,
                    "mtime": v.mtime,
                    "hash": v.hash_value,
                    "group_id": v.group_id,
                }
                for k, v in self.entries.items()
            },
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> DedupCache:
        """Load cache from file."""
        cache = cls()
        if not path.exists():
            return cache
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cache.last_updated = data.get("updated", 0)
            for key, entry in data.get("entries", {}).items():
                cache.entries[key] = CacheEntry(
                    path=entry["path"],
                    size=entry["size"],
                    mtime=entry["mtime"],
                    hash_value=entry["hash"],
                    group_id=entry.get("group_id", -1),
                )
        except (json.JSONDecodeError, OSError):
            pass
        return cache

    @property
    def count(self) -> int:
        return len(self.entries)

    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "entries": self.count,
            "last_updated": self.last_updated,
        }


def format_cache_stats(cache: DedupCache) -> str:
    """Format cache stats as text."""
    import datetime

    dt = (
        datetime.datetime.fromtimestamp(cache.last_updated).strftime("%Y-%m-%d %H:%M")
        if cache.last_updated > 0
        else "never"
    )
    return f"Dedup Cache: {cache.count:,} entries, last updated: {dt}"
