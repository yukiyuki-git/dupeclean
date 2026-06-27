"""File search module for DupeClean.

Search for files by name, extension, size, or content pattern
within a scanned directory tree.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class SearchQuery:
    """A file search query."""

    name_pattern: str | None = None  # glob pattern
    extension: str | None = None  # without dot
    min_size: int | None = None
    max_size: int | None = None
    content_pattern: str | None = None  # regex
    case_sensitive: bool = False


@dataclass
class SearchResult:
    """Search results."""

    query: SearchQuery
    matches: list[FileInfo] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.matches)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.matches)


def search_files(
    files: list[FileInfo],
    query: SearchQuery,
) -> SearchResult:
    """Search files matching query criteria.

    Args:
        files: List of files to search.
        query: Search criteria.

    Returns:
        SearchResult with matching files.
    """
    result = SearchResult(query=query)

    for fi in files:
        if _matches_query(fi, query):
            result.matches.append(fi)

    result.matches.sort(key=lambda f: f.size, reverse=True)
    return result


def _matches_query(fi: FileInfo, query: SearchQuery) -> bool:
    """Check if a file matches search criteria."""
    name = fi.path.name

    # Name pattern
    if query.name_pattern:
        flags = 0 if query.case_sensitive else re.IGNORECASE
        if not fnmatch.fnmatch(name, query.name_pattern):
            # Also try regex
            try:
                if not re.search(query.name_pattern, name, flags):
                    return False
            except re.error:
                return False

    # Extension
    if query.extension:
        ext = query.extension.lstrip(".").lower()
        if fi.ext.lstrip(".").lower() != ext:
            return False

    # Size range
    if query.min_size is not None and fi.size < query.min_size:
        return False
    return not (query.max_size is not None and fi.size > query.max_size)


def search_by_name(files: list[FileInfo], pattern: str) -> SearchResult:
    """Search files by name pattern."""
    return search_files(files, SearchQuery(name_pattern=pattern))


def search_by_extension(files: list[FileInfo], ext: str) -> SearchResult:
    """Search files by extension."""
    return search_files(files, SearchQuery(extension=ext))


def search_by_size(
    files: list[FileInfo],
    min_size: int | None = None,
    max_size: int | None = None,
) -> SearchResult:
    """Search files by size range."""
    return search_files(files, SearchQuery(min_size=min_size, max_size=max_size))


def format_search_result(result: SearchResult) -> str:
    """Format search results as text."""
    if not result.matches:
        return "No files found matching query."

    lines = [
        f"Search results: {result.count:,} files, {format_size(result.total_size)} total",
        "",
    ]

    for fi in result.matches[:50]:
        lines.append(f"  {fi.size_display:>10s}  {fi.path.name}  [dim]{fi.path.parent}[/]")

    if result.count > 50:
        lines.append(f"\n  ... and {result.count - 50} more files")

    return "\n".join(lines)
