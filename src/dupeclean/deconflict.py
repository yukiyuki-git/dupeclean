"""File deconfliction module for DupeClean.

Handle file name conflicts during batch operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConflictResolution:
    """Result of resolving a file conflict."""

    original: Path
    resolved: Path
    strategy: str
    was_conflict: bool


def resolve_conflict(
    target: Path,
    strategy: str = "rename",
) -> ConflictResolution:
    """Resolve a file name conflict.

    Args:
        target: Desired target path.
        strategy: "rename", "overwrite", "skip", "number".

    Returns:
        ConflictResolution with resolved path.
    """
    if not target.exists():
        return ConflictResolution(
            original=target,
            resolved=target,
            strategy=strategy,
            was_conflict=False,
        )

    if strategy == "overwrite":
        return ConflictResolution(
            original=target,
            resolved=target,
            strategy="overwrite",
            was_conflict=True,
        )

    if strategy == "skip":
        return ConflictResolution(
            original=target,
            resolved=target,
            strategy="skip",
            was_conflict=True,
        )

    if strategy == "number":
        resolved = _numbered_path(target)
        return ConflictResolution(
            original=target,
            resolved=resolved,
            strategy="number",
            was_conflict=True,
        )

    # Default: rename with counter
    resolved = _numbered_path(target)
    return ConflictResolution(
        original=target,
        resolved=resolved,
        strategy="rename",
        was_conflict=True,
    )


def _numbered_path(path: Path) -> Path:
    """Generate a numbered path to avoid conflicts."""
    counter = 1
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def resolve_batch_conflicts(
    targets: list[Path],
    strategy: str = "rename",
) -> list[ConflictResolution]:
    """Resolve conflicts for a batch of target paths.

    Tracks already-resolved paths to avoid conflicts
    between items in the batch.
    """
    resolved_paths: set[Path] = set()
    results: list[ConflictResolution] = []

    for target in targets:
        resolution = resolve_conflict(target, strategy)

        # Also check against already-resolved paths
        while resolution.resolved in resolved_paths and strategy not in ("skip", "overwrite"):
            resolution = ConflictResolution(
                original=target,
                resolved=_numbered_path(resolution.resolved),
                strategy=strategy,
                was_conflict=True,
            )

        resolved_paths.add(resolution.resolved)
        results.append(resolution)

    return results


def format_conflict_report(
    resolutions: list[ConflictResolution],
) -> str:
    """Format conflict resolutions as text."""
    conflicts = [r for r in resolutions if r.was_conflict]
    if not conflicts:
        return "No conflicts detected."

    lines = [
        f"Conflicts: {len(conflicts)} of {len(resolutions)} files had name conflicts",
        "",
    ]

    for r in conflicts[:20]:
        lines.append(f"  {r.original.name} -> {r.resolved.name} [{r.strategy}]")

    if len(conflicts) > 20:
        lines.append(f"\n  ... and {len(conflicts) - 20} more")

    return "\n".join(lines)
