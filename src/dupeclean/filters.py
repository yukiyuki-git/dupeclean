"""File filter module for DupeClean.

Advanced file filtering with composable filter chains.
"""

from __future__ import annotations

import fnmatch
import re
from collections.abc import Callable
from dataclasses import dataclass

from .models import FileInfo


@dataclass
class FileFilter:
    """A composable file filter."""

    name: str
    predicate: Callable[[FileInfo], bool]

    def __call__(self, fi: FileInfo) -> bool:
        return self.predicate(fi)

    def __and__(self, other: FileFilter) -> FileFilter:
        return FileFilter(
            f"{self.name} AND {other.name}",
            lambda fi: self(fi) and other(fi),
        )

    def __or__(self, other: FileFilter) -> FileFilter:
        return FileFilter(
            f"{self.name} OR {other.name}",
            lambda fi: self(fi) or other(fi),
        )

    def __invert__(self) -> FileFilter:
        return FileFilter(f"NOT {self.name}", lambda fi: not self(fi))


def by_extension(*exts: str) -> FileFilter:
    """Filter by file extension."""
    normalized = {e.lstrip(".").lower() for e in exts}
    return FileFilter(
        f"ext={exts}",
        lambda fi: fi.ext.lstrip(".").lower() in normalized,
    )


def by_name(pattern: str) -> FileFilter:
    """Filter by filename pattern (glob)."""
    return FileFilter(
        f"name={pattern}",
        lambda fi: fnmatch.fnmatch(fi.path.name, pattern),
    )


def by_name_regex(pattern: str) -> FileFilter:
    """Filter by filename regex."""
    compiled = re.compile(pattern)
    return FileFilter(
        f"regex={pattern}",
        lambda fi: bool(compiled.search(fi.path.name)),
    )


def by_min_size(size: int) -> FileFilter:
    """Filter files larger than size."""
    return FileFilter(
        f"min_size={size}",
        lambda fi: fi.size >= size,
    )


def by_max_size(size: int) -> FileFilter:
    """Filter files smaller than size."""
    return FileFilter(
        f"max_size={size}",
        lambda fi: fi.size <= size,
    )


def by_min_age(days: float) -> FileFilter:
    """Filter files older than days."""
    import time

    cutoff = time.time() - (days * 86400)
    return FileFilter(
        f"min_age={days}d",
        lambda fi: fi.mtime < cutoff,
    )


def by_max_age(days: float) -> FileFilter:
    """Filter files newer than days."""
    import time

    cutoff = time.time() - (days * 86400)
    return FileFilter(
        f"max_age={days}d",
        lambda fi: fi.mtime >= cutoff,
    )


def is_empty() -> FileFilter:
    """Filter empty files."""
    return FileFilter("empty", lambda fi: fi.size == 0)


def is_symlink() -> FileFilter:
    """Filter symbolic links."""
    return FileFilter("symlink", lambda fi: fi.is_symlink)


def has_hash() -> FileFilter:
    """Filter files that have been hashed."""
    return FileFilter(
        "has_hash",
        lambda fi: fi.hash_for_dedup is not None,
    )


def apply_filter(files: list[FileInfo], file_filter: FileFilter) -> list[FileInfo]:
    """Apply a filter to a file list."""
    return [fi for fi in files if file_filter(fi)]


def filter_summary(original: int, filtered: int, name: str) -> str:
    """Format filter result summary."""
    pct = (filtered / original * 100) if original else 0
    return f"Filter '{name}': {filtered:,}/{original:,} files ({pct:.1f}%)"
