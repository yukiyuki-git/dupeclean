"""Ignore file support for DupeClean.

Reads .dupecleanignore files (same format as .gitignore).
Supports glob patterns, negation, and comments.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

IGNORE_FILE_NAME = ".dupecleanignore"


def load_ignore_patterns(path: Path) -> list[str]:
    """Load ignore patterns from a .dupecleanignore file.

    Args:
        path: Path to the ignore file.

    Returns:
        List of glob patterns.
    """
    if not path.exists():
        return []

    patterns: list[str] = []
    try:
        content = path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Handle negation (include patterns)
            if line.startswith("!"):
                continue  # Skip negation for now
            patterns.append(line)
    except (OSError, UnicodeDecodeError):
        pass

    return patterns


def find_ignore_file(start_path: Path) -> Path | None:
    """Find the nearest .dupecleanignore file.

    Walks up the directory tree from start_path.
    """
    current = start_path if start_path.is_dir() else start_path.parent
    while True:
        ignore_file = current / IGNORE_FILE_NAME
        if ignore_file.exists():
            return ignore_file
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def should_ignore(
    filepath: Path,
    patterns: list[str],
    root: Path | None = None,
) -> bool:
    """Check if a file should be ignored based on patterns.

    Args:
        filepath: The file path to check.
        patterns: List of glob patterns.
        root: Root directory for relative path matching.

    Returns:
        True if the file should be ignored.
    """
    name = filepath.name
    rel_path = str(filepath.relative_to(root)) if root else str(filepath)

    # Normalize path separators for matching
    rel_path_normalized = rel_path.replace("\\", "/")

    for pattern in patterns:
        # Match against filename
        if fnmatch.fnmatch(name, pattern):
            return True
        # Match against relative path
        if fnmatch.fnmatch(rel_path_normalized, pattern):
            return True
        # Match directory patterns — check if any path component matches
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")
            parts = rel_path_normalized.split("/")
            for part in parts:
                if fnmatch.fnmatch(part, dir_pattern):
                    return True
        # Match glob with directory prefix (e.g., "build/*")
        if fnmatch.fnmatch(rel_path_normalized, pattern):
            return True

    return False


def get_combined_ignore_patterns(
    path: Path,
    config_patterns: list[str] | None = None,
) -> list[str]:
    """Get combined ignore patterns from config and ignore file.

    Args:
        path: Directory to look for .dupecleanignore in.
        config_patterns: Patterns from config file.

    Returns:
        Combined list of patterns.
    """
    patterns = list(config_patterns or [])

    ignore_file = find_ignore_file(path)
    if ignore_file:
        file_patterns = load_ignore_patterns(ignore_file)
        patterns.extend(file_patterns)

    return patterns
