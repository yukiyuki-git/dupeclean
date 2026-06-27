"""File deduplication group conflict resolver for DupeClean.

Resolve conflicts in duplicate groups.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup, FileInfo


@dataclass
class Conflict:
    """A conflict in a group."""

    group_id: int
    conflict_type: str  # "size_mismatch", "missing_file", "hash_mismatch"
    description: str
    files: list[FileInfo] = field(default_factory=list)


@dataclass
class Resolution:
    """Resolution of a conflict."""

    conflict: Conflict
    resolution_type: str  # "skip", "re-scan", "remove"
    description: str = ""


@dataclass
class ConflictResolver:
    """Resolve conflicts in groups."""

    conflicts: list[Conflict] = field(default_factory=list)
    resolutions: list[Resolution] = field(default_factory=list)

    def detect(self, groups: list[DuplicateGroup]) -> list[Conflict]:
        """Detect conflicts in groups."""
        self.conflicts.clear()
        for group in groups:
            sizes = set(f.size for f in group.files)
            if len(sizes) > 1:
                self.conflicts.append(
                    Conflict(
                        group_id=group.group_id,
                        conflict_type="size_mismatch",
                        description=f"Mixed sizes: {sizes}",
                        files=group.files,
                    )
                )
            for fi in group.files:
                if not fi.path.exists():
                    self.conflicts.append(
                        Conflict(
                            group_id=group.group_id,
                            conflict_type="missing_file",
                            description=f"Missing: {fi.path}",
                            files=[fi],
                        )
                    )
                    break
        return self.conflicts

    def auto_resolve(self) -> list[Resolution]:
        """Auto-resolve detected conflicts."""
        self.resolutions.clear()
        for conflict in self.conflicts:
            if conflict.conflict_type == "missing_file":
                self.resolutions.append(
                    Resolution(
                        conflict=conflict,
                        resolution_type="re-scan",
                        description="Re-scan to update file list",
                    )
                )
            elif conflict.conflict_type == "size_mismatch":
                self.resolutions.append(
                    Resolution(
                        conflict=conflict,
                        resolution_type="skip",
                        description="Skip group due to size mismatch",
                    )
                )
        return self.resolutions

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)


def format_conflicts(resolver: ConflictResolver) -> str:
    """Format conflicts as text."""
    if not resolver.has_conflicts:
        return "No conflicts detected."
    lines = [f"Conflicts: {resolver.conflict_count}", ""]
    for c in resolver.conflicts:
        lines.append(f"  [{c.conflict_type}] Group #{c.group_id}: {c.description}")
    return "\n".join(lines)
