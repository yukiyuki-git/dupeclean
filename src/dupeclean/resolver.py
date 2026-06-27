"""File deduplication duplicate resolver module for DupeClean.

Resolve duplicate groups by applying strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo, format_size


@dataclass
class Resolution:
    """Resolution of a duplicate group."""

    group_id: int
    strategy: str
    keeper: FileInfo
    resolved: list[FileInfo] = field(default_factory=list)
    space_saved: int = 0

    @property
    def saved_display(self) -> str:
        return format_size(self.space_saved)


@dataclass
class ResolutionResult:
    """Result of resolving multiple groups."""

    resolutions: list[Resolution] = field(default_factory=list)

    @property
    def total_resolved(self) -> int:
        return len(self.resolutions)

    @property
    def total_saved(self) -> int:
        return sum(r.space_saved for r in self.resolutions)


def resolve_group(
    group: DuplicateGroup,
    strategy: str = "shortest",
) -> Resolution:
    """Resolve a single duplicate group."""
    if strategy == "newest":
        keep_idx = max(range(group.count), key=lambda i: group.files[i].mtime)
    elif strategy == "oldest":
        keep_idx = min(range(group.count), key=lambda i: group.files[i].mtime)
    else:
        keep_idx = min(range(group.count), key=lambda i: len(str(group.files[i].path)))

    keeper = group.files[keep_idx]
    resolved = [f for i, f in enumerate(group.files) if i != keep_idx]

    return Resolution(
        group_id=group.group_id,
        strategy=strategy,
        keeper=keeper,
        resolved=resolved,
        space_saved=sum(f.size for f in resolved),
    )


def resolve_groups(
    groups: list[DuplicateGroup],
    strategy: str = "shortest",
) -> ResolutionResult:
    """Resolve multiple duplicate groups."""
    result = ResolutionResult()
    for group in groups:
        if len(group.files) >= 2:
            result.resolutions.append(resolve_group(group, strategy))
    return result


def format_resolution(result: ResolutionResult) -> str:
    """Format resolution result as text."""
    return f"Resolved: {result.total_resolved} groups, {format_size(result.total_saved)} saved"
