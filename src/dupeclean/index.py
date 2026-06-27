"""File deduplication index module for DupeClean.

Index files for fast lookup during dedup operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class FileIndex:
    """Index of files for fast lookup."""

    by_path: dict[str, FileInfo] = field(default_factory=dict)
    by_size: dict[int, list[FileInfo]] = field(default_factory=dict)
    by_hash: dict[str, list[FileInfo]] = field(default_factory=dict)
    by_ext: dict[str, list[FileInfo]] = field(default_factory=dict)

    def add(self, fi: FileInfo) -> None:
        """Add a file to the index."""
        self.by_path[str(fi.path)] = fi
        self.by_size.setdefault(fi.size, []).append(fi)
        if fi.hash_for_dedup:
            self.by_hash.setdefault(fi.hash_for_dedup, []).append(fi)
        ext = fi.ext or "(none)"
        self.by_extension.setdefault(ext, []).append(fi)

    @property
    def by_extension(self) -> dict[str, list[FileInfo]]:
        return self.by_ext

    @property
    def total_files(self) -> int:
        return len(self.by_path)

    @property
    def total_size(self) -> int:
        return sum(fi.size for fi in self.by_path.values())

    def get_size_duplicates(self) -> dict[int, list[FileInfo]]:
        """Get files grouped by size (potential duplicates)."""
        return {size: files for size, files in self.by_size.items() if len(files) >= 2 and size > 0}

    def get_hash_duplicates(self) -> dict[str, list[FileInfo]]:
        """Get files grouped by hash (confirmed duplicates)."""
        return {h: files for h, files in self.by_hash.items() if len(files) >= 2}

    def get_by_extension(self, ext: str) -> list[FileInfo]:
        """Get files by extension."""
        return self.by_ext.get(ext, [])


def build_index(files: list[FileInfo]) -> FileIndex:
    """Build a file index from a list of files."""
    index = FileIndex()
    for fi in files:
        index.add(fi)
    return index


def format_index_stats(index: FileIndex) -> str:
    """Format index statistics as text."""
    size_dupes = index.get_size_duplicates()
    hash_dupes = index.get_hash_duplicates()

    lines = [
        f"File Index: {index.total_files:,} files, {format_size(index.total_size)}",
        f"  Extensions: {len(index.by_extension)}",
        f"  Size-based potential dupes: {len(size_dupes)} groups",
        f"  Hash-confirmed dupes: {len(hash_dupes)} groups",
    ]
    return "\n".join(lines)
