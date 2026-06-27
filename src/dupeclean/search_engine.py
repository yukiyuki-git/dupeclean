"""File deduplication search engine for DupeClean.

Advanced search capabilities for finding files.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class SearchQuery:
    """A search query."""
    name_pattern: str | None = None
    extension: str | None = None
    min_size: int | None = None
    max_size: int | None = None
    min_age_days: float | None = None
    max_age_days: float | None = None
    content_regex: str | None = None
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
    """Search files matching query criteria."""
    result = SearchResult(query=query)
    import time

    now = time.time()

    for fi in files:
        # Name pattern
        if query.name_pattern and not fnmatch.fnmatch(fi.path.name, query.name_pattern):
            try:
                if not re.search(query.name_pattern, fi.path.name):
                    continue
            except re.error:
                continue

        # Extension
        if query.extension:
            ext = query.extension.lstrip(".").lower()
            if fi.ext.lstrip(".").lower() != ext:
                continue

        # Size range
        if query.min_size is not None and fi.size < query.min_size:
            continue
        if query.max_size is not None and fi.size > query.max_size:
            continue

        # Age range
        if query.min_age_days is not None:
            age_days = (now - fi.mtime) / 86400 if fi.mtime > 0 else 0
            if age_days < query.min_age_days:
                continue
        if query.max_age_days is not None:
            age_days = (now - fi.mtime) / 86400 if fi.mtime > 0 else 0
            if age_days > query.max_age_days:
                continue

        result.matches.append(fi)

    result.matches.sort(key=lambda f: f.size, reverse=True)
    return result


def format_search_result(result: SearchResult) -> str:
    """Format search results as text."""
    if not result.matches:
        return "No files found matching query."

    lines = [
        f"Search: {result.count:,} matches, "
        f"{format_size(result.total_size)} total",
        "",
    ]
    for fi in result.matches[:20]:
        lines.append(
            f"  {fi.size_display:>10s}  {fi.path.name}  "
            f"[dim]{fi.path.parent}[/]"
        )
    if result.count > 20:
        lines.append(f"\n  ... and {result.count - 20} more")
    return "\n".join(lines)
