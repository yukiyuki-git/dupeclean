"""Fuzzy filename matcher for finding similar (not identical) files.

Detects files that likely belong together based on name similarity:
- "photo (1).jpg" / "photo (2).jpg"
- "report_v1.pdf" / "report_v2.pdf"
- "IMG_20240101.jpg" / "IMG_20240102.jpg"
- "song.mp3" / "song (copy).mp3"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from .models import FileInfo, format_size

# Common suffixes added by OS/browsers when copying
COPY_SUFFIXES = [
    r"\s*\(\d+\)",  # (1), (2), etc.
    r"\s*-\s*Copy",  # - Copy
    r"\s*copy\s*\d*",  # copy, copy2
    r"\s*_\d+",  # _1, _2
    r"\s*\(copy\)",  # (copy)
    r"\s*副本",  # Chinese "copy"
    r"\s*\[duplicate\]",  # [duplicate]
    r"\s*\(conflict\)",  # (conflict)
]

COPY_PATTERN = re.compile("|".join(COPY_SUFFIXES), re.IGNORECASE)

# Pattern to extract version numbers
VERSION_PATTERN = re.compile(r"[_\-\s]v?(\d+(?:\.\d+)*)", re.IGNORECASE)

# Pattern to extract trailing numbers
TRAILING_NUM_PATTERN = re.compile(r"[_\-\s](\d+)$")


@dataclass
class SimilarGroup:
    """A group of files with similar names."""

    group_id: int
    base_name: str
    files: list[FileInfo] = field(default_factory=list)
    similarity: float = 0.0  # 0.0 to 1.0

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def total_size_display(self) -> str:
        return format_size(self.total_size)


def normalize_filename(name: str) -> str:
    """Normalize a filename for comparison.

    Strips copy suffixes, version numbers, and common variations.
    """
    # Remove extension
    stem = Path(name).stem

    # Remove copy suffixes
    stem = COPY_PATTERN.sub("", stem)

    # Remove trailing numbers that look like copies
    stem = TRAILING_NUM_PATTERN.sub("", stem)

    # Normalize whitespace and case
    stem = stem.strip().lower()

    # Remove common separators
    stem = re.sub(r"[\s_\-]+", " ", stem)

    return stem


def similarity_score(name1: str, name2: str) -> float:
    """Calculate similarity between two filenames.

    Returns a score from 0.0 (completely different) to 1.0 (identical).
    """
    norm1 = normalize_filename(name1)
    norm2 = normalize_filename(name2)

    if not norm1 or not norm2:
        return 0.0

    return SequenceMatcher(None, norm1, norm2).ratio()


def extract_version(name: str) -> str | None:
    """Extract version number from filename.

    Returns version string like "1.0" or "2", or None.
    """
    match = VERSION_PATTERN.search(name)
    return match.group(1) if match else None


def find_similar_names(
    files: list[FileInfo],
    threshold: float = 0.7,
) -> list[SimilarGroup]:
    """Find groups of files with similar names.

    Args:
        files: List of files to analyze.
        threshold: Minimum similarity score to group (0.0-1.0).

    Returns:
        List of SimilarGroup sorted by group size descending.
    """
    if len(files) < 2:
        return []

    # Group by extension first (files with different extensions
    # are rarely near-duplicates)
    by_ext: dict[str, list[FileInfo]] = {}
    for fi in files:
        ext = fi.ext or "(none)"
        by_ext.setdefault(ext, []).append(fi)

    groups: list[SimilarGroup] = []
    group_id = 0

    for _ext, ext_files in by_ext.items():
        if len(ext_files) < 2:
            continue

        # Compare all pairs
        used: set[int] = set()  # indices of files already grouped

        for i, fi_a in enumerate(ext_files):
            if i in used:
                continue

            similar: list[FileInfo] = [fi_a]
            scores: list[float] = []
            name_a = fi_a.path.name

            for j in range(i + 1, len(ext_files)):
                if j in used:
                    continue
                fi_b = ext_files[j]
                score = similarity_score(name_a, fi_b.path.name)
                if score >= threshold:
                    similar.append(fi_b)
                    scores.append(score)
                    used.add(j)

            if len(similar) >= 2:
                used.add(i)
                avg_score = sum(scores) / len(scores) if scores else 0.0
                base = normalize_filename(name_a)
                groups.append(
                    SimilarGroup(
                        group_id=group_id,
                        base_name=base,
                        files=similar,
                        similarity=avg_score,
                    )
                )
                group_id += 1

    groups.sort(key=lambda g: g.count, reverse=True)
    return groups


def find_copy_pairs(
    files: list[FileInfo],
) -> list[tuple[FileInfo, FileInfo]]:
    """Find obvious copy pairs (e.g., 'file.txt' and 'file (1).txt').

    Returns list of (original, copy) tuples.
    """
    pairs: list[tuple[FileInfo, FileInfo]] = []
    by_stem: dict[str, list[FileInfo]] = {}

    for fi in files:
        stem = fi.path.stem.lower()
        # Strip copy suffixes to get base name
        base = COPY_PATTERN.sub("", stem).strip()
        ext = fi.ext
        key = f"{base}.{ext}"
        by_stem.setdefault(key, []).append(fi)

    for _key, group in by_stem.items():
        if len(group) < 2:
            continue
        # Sort by name length (shorter = likely original)
        group.sort(key=lambda f: len(f.path.name))
        original = group[0]
        for copy in group[1:]:
            pairs.append((original, copy))

    return pairs
