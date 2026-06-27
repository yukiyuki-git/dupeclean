"""File deduplication hash cache for DupeClean.

Cache file hashes for incremental scan performance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HashCacheEntry:
    """A cached hash entry."""

    path: str
    size: int
    mtime: float
    hash_value: str


@dataclass
class HashCache:
    """Persistent hash cache for incremental scans."""

    entries: dict[str, HashCacheEntry] = field(default_factory=dict)

    def get(self, path: Path, size: int, mtime: float) -> str | None:
        """Get cached hash if valid."""
        entry = self.entries.get(str(path))
        if entry and entry.size == size and entry.mtime == mtime:
            return entry.hash_value
        return None

    def put(self, path: Path, size: int, mtime: float, hash_value: str) -> None:
        """Cache a hash value."""
        self.entries[str(path)] = HashCacheEntry(
            path=str(path), size=size, mtime=mtime, hash_value=hash_value
        )

    def invalidate(self, path: Path) -> None:
        """Remove a cached entry."""
        self.entries.pop(str(path), None)

    @property
    def count(self) -> int:
        return len(self.entries)

    def save(self, path: Path) -> None:
        """Save cache to file."""
        data = {
            "version": 1,
            "entries": {
                k: {"path": v.path, "size": v.size, "mtime": v.mtime, "hash": v.hash_value}
                for k, v in self.entries.items()
            },
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> HashCache:
        """Load cache from file."""
        cache = cls()
        if not path.exists():
            return cache
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for key, entry in data.get("entries", {}).items():
                cache.entries[key] = HashCacheEntry(
                    path=entry["path"],
                    size=entry["size"],
                    mtime=entry["mtime"],
                    hash_value=entry["hash"],
                )
        except (json.JSONDecodeError, OSError):
            pass
        return cache


def format_hash_cache_stats(cache: HashCache) -> str:
    """Format cache stats as text."""
    return f"Hash Cache: {cache.count:,} entries"
