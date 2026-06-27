"""File deduplication scan cache for DupeClean.

Cache scan results for incremental rescanning.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo


@dataclass
class ScanCacheEntry:
    """A cached scan entry."""

    path: str
    size: int
    mtime: float
    scan_time: float


@dataclass
class ScanCache:
    """Cache for scan results."""

    entries: dict[str, ScanCacheEntry] = field(default_factory=dict)
    last_scan: float = 0.0

    def add(self, fi: FileInfo) -> None:
        """Cache a file entry."""
        self.entries[str(fi.path)] = ScanCacheEntry(
            path=str(fi.path),
            size=fi.size,
            mtime=fi.mtime,
            scan_time=time.time(),
        )

    def get(self, path: Path) -> ScanCacheEntry | None:
        """Get cached entry."""
        return self.entries.get(str(path))

    def is_valid(self, fi: FileInfo) -> bool:
        """Check if cached entry matches current file."""
        entry = self.get(fi.path)
        if entry is None:
            return False
        return entry.size == fi.size and entry.mtime == fi.mtime

    @property
    def count(self) -> int:
        return len(self.entries)

    def save(self, path: Path) -> None:
        """Save cache to file."""
        data = {
            "version": 1,
            "last_scan": self.last_scan,
            "entries": {
                k: {
                    "path": v.path,
                    "size": v.size,
                    "mtime": v.mtime,
                    "scan_time": v.scan_time,
                }
                for k, v in self.entries.items()
            },
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> ScanCache:
        """Load cache from file."""
        cache = cls()
        if not path.exists():
            return cache
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cache.last_scan = data.get("last_scan", 0)
            for key, entry in data.get("entries", {}).items():
                cache.entries[key] = ScanCacheEntry(
                    path=entry["path"],
                    size=entry["size"],
                    mtime=entry["mtime"],
                    scan_time=entry.get("scan_time", 0),
                )
        except (json.JSONDecodeError, OSError):
            pass
        return cache

    def get_unchanged(self, files: list[FileInfo]) -> list[FileInfo]:
        """Get files that haven't changed since last scan."""
        return [fi for fi in files if self.is_valid(fi)]

    def get_changed(self, files: list[FileInfo]) -> list[FileInfo]:
        """Get files that have changed since last scan."""
        return [fi for fi in files if not self.is_valid(fi)]


def format_scan_cache(cache: ScanCache) -> str:
    """Format scan cache as text."""
    import datetime

    last = (
        datetime.datetime.fromtimestamp(cache.last_scan).strftime("%Y-%m-%d %H:%M")
        if cache.last_scan > 0
        else "never"
    )
    return f"Scan Cache: {cache.count:,} entries, last scan: {last}"
