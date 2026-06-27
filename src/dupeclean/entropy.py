"""Entropy analysis module for DupeClean.

Calculate file entropy to detect:
- Encrypted files (high entropy ~8.0)
- Compressed files (high entropy ~7.9)
- Normal text/code files (lower entropy ~4-5)
- Empty or sparse files (very low entropy)
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo


@dataclass
class EntropyResult:
    """Entropy analysis result for a file."""

    path: Path
    entropy: float  # 0.0 to 8.0 (bits per byte)
    file_size: int
    category: str  # "low", "normal", "high", "encrypted"

    @property
    def is_likely_encrypted(self) -> bool:
        return self.entropy > 7.5

    @property
    def is_likely_compressed(self) -> bool:
        return 7.0 < self.entropy <= 7.5

    @property
    def description(self) -> str:
        if self.entropy < 1.0:
            return "Empty or sparse"
        if self.entropy < 4.0:
            return "Low entropy (structured data)"
        if self.entropy < 6.0:
            return "Normal (text/code)"
        if self.entropy < 7.0:
            return "Moderate entropy"
        if self.entropy < 7.5:
            return "High entropy (compressed?)"
        return "Very high entropy (encrypted?)"


def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of byte data.

    Args:
        data: Raw bytes to analyze.

    Returns:
        Entropy in bits per byte (0.0 to 8.0).
    """
    if not data:
        return 0.0

    length = len(data)
    counts = Counter(data)
    entropy = 0.0

    for count in counts.values():
        if count > 0:
            probability = count / length
            entropy -= probability * math.log2(probability)

    return entropy


def analyze_file_entropy(
    filepath: Path,
    sample_size: int = 8192,
) -> EntropyResult | None:
    """Analyze entropy of a file.

    Reads a sample from the beginning of the file.

    Args:
        filepath: Path to file.
        sample_size: Bytes to read for analysis.

    Returns:
        EntropyResult or None if file cannot be read.
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read(sample_size)
    except (OSError, PermissionError):
        return None

    entropy = calculate_entropy(data)
    file_size = filepath.stat().st_size

    if entropy < 1.0:
        category = "empty"
    elif entropy < 5.0:
        category = "low"
    elif entropy < 7.0:
        category = "normal"
    elif entropy < 7.5:
        category = "high"
    else:
        category = "encrypted"

    return EntropyResult(
        path=filepath,
        entropy=entropy,
        file_size=file_size,
        category=category,
    )


def find_high_entropy_files(
    files: list[FileInfo],
    threshold: float = 7.0,
    sample_size: int = 8192,
) -> list[EntropyResult]:
    """Find files with entropy above a threshold.

    Args:
        files: List of FileInfo to analyze.
        threshold: Minimum entropy to include.
        sample_size: Bytes to read per file.

    Returns:
        List of EntropyResult sorted by entropy descending.
    """
    results: list[EntropyResult] = []

    for fi in files:
        result = analyze_file_entropy(fi.path, sample_size)
        if result and result.entropy >= threshold:
            results.append(result)

    results.sort(key=lambda r: r.entropy, reverse=True)
    return results


def categorize_by_entropy(
    files: list[FileInfo],
    sample_size: int = 8192,
) -> dict[str, list[EntropyResult]]:
    """Categorize files by their entropy level.

    Returns:
        Dict with keys: "empty", "low", "normal", "high", "encrypted".
    """
    categories: dict[str, list[EntropyResult]] = {
        "empty": [],
        "low": [],
        "normal": [],
        "high": [],
        "encrypted": [],
    }

    for fi in files:
        result = analyze_file_entropy(fi.path, sample_size)
        if result:
            categories[result.category].append(result)

    return categories
