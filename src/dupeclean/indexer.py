"""File deduplication file indexer module for DupeClean.

Build and maintain file indexes for fast lookups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class FileIndex:
    """A file index for fast lookups."""

    by_path: dict[str, FileInfo] = field(default_factory=dict)
    by_size: dict[int, list[FileInfo]] = field(default_factory=dict)
    by_ext: dict[str, list[FileInfo]] = field(default_factory=dict)
    by_hash: dict[str, list[FileInfo]] = field(default_factory=dict)

    def add(self, fi: FileInfo) -> None:
        """Add a file to the index."""
        self.by_path[str(fi.path)] = fi
        self.by_size.setdefault(fi.size, []).append(fi)
        ext = fi.ext or "(none)"
        self.by_ext.setdefault(ext, []).append(fi)
        if fi.hash_for_dedup:
            self.by_hash.setdefault(fi.hash_for_dedup, []).append(fi)

    def get_by_path(self, path: Path) -> FileInfo | None:
        return self.by_path.get(str(path))

    def get_by_size(self, size: int) -> list[FileInfo]:
        return self.by_size.get(size, [])

    def get_by_ext(self, ext: str) -> list[FileInfo]:
        return self.by_ext.get(ext, [])

    def get_duplicates_by_size(self) -> dict[int, list[FileInfo]]:
        return {s: f for s, f in self.by_size.items() if len(f) >= 2 and s > 0}

    def get_duplicates_by_hash(self) -> dict[str, list[FileInfo]]:
        return {h: f for h, f in self.by_hash.items() if len(f) >= 2}

    @property
    def total_files(self) -> int:
        return len(self.by_path)

    @property
    def total_size(self) -> int:
        return sum(fi.size for fi in self.by_path.values())

    @property
    def extension_count(self) -> int:
        return len(self.by_ext)


def build_index(files: list[FileInfo]) -> FileIndex:
    """Build a file index from a list of files."""
    index = FileIndex()
    for fi in files:
        index.add(fi)
    return index


def format_index(index: FileIndex) -> str:
    """Format index statistics as text."""
    return (
        f"File Index: {index.total_files:,} files, "
        f"{format_size(index.total_size)}, "
        f"{index.extension_count} extensions"
    )
