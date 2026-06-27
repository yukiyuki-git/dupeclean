"""File deduplication by content similarity for DupeClean.

Find files that are similar (but not identical) based on
content analysis. Useful for finding near-duplicate documents,
images with slight edits, etc.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo


@dataclass
class SimilarityResult:
    """Similarity between two files."""
    file_a: Path
    file_b: Path
    similarity: float  # 0.0 to 1.0
    method: str  # "rolling_hash", "byte_frequency", "chunk_compare"


def byte_frequency_hash(
    filepath: Path, sample_size: int = 8192
) -> bytes | None:
    """Compute byte frequency histogram as a hash.

    Similar files tend to have similar byte distributions.
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read(sample_size)
    except OSError:
        return None

    freq = [0] * 256
    for byte in data:
        freq[byte] += 1

    # Normalize
    total = len(data) if data else 1
    normalized = bytes(f * 255 // total for f in freq)
    return normalized


def chunk_hash(
    filepath: Path, chunk_size: int = 4096, num_chunks: int = 8
) -> list[str] | None:
    """Compute hashes of evenly-spaced chunks.

    Files with similar structure will have matching chunks.
    """
    try:
        file_size = filepath.stat().st_size
    except OSError:
        return None

    if file_size == 0:
        return []

    hashes = []
    try:
        with open(filepath, "rb") as f:
            for i in range(num_chunks):
                offset = int(file_size * i / num_chunks)
                f.seek(offset)
                chunk = f.read(chunk_size)
                h = hashlib.md5(chunk).hexdigest()
                hashes.append(h)
    except OSError:
        return None

    return hashes


def compare_byte_frequency(
    file_a: Path, file_b: Path
) -> float:
    """Compare byte frequency distributions.

    Returns similarity score 0.0 to 1.0.
    """
    hash_a = byte_frequency_hash(file_a)
    hash_b = byte_frequency_hash(file_b)

    if hash_a is None or hash_b is None:
        return 0.0

    if len(hash_a) != len(hash_b):
        return 0.0

    # Cosine-like similarity
    dot_product = sum(a * b for a, b in zip(hash_a, hash_b, strict=True))
    norm_a = sum(a * a for a in hash_a) ** 0.5
    norm_b = sum(b * b for b in hash_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def compare_chunks(file_a: Path, file_b: Path) -> float:
    """Compare chunk hashes of two files.

    Returns fraction of matching chunks.
    """
    chunks_a = chunk_hash(file_a)
    chunks_b = chunk_hash(file_b)

    if chunks_a is None or chunks_b is None:
        return 0.0

    if not chunks_a and not chunks_b:
        return 1.0

    if len(chunks_a) != len(chunks_b):
        return 0.0

    matches = sum(
        1 for a, b in zip(chunks_a, chunks_b, strict=True) if a == b
    )
    return matches / len(chunks_a)


def find_similar_content(
    files: list[FileInfo],
    threshold: float = 0.8,
    method: str = "chunk",
) -> list[SimilarityResult]:
    """Find files with similar content.

    Args:
        files: Files to compare.
        threshold: Minimum similarity to report.
        method: "byte_freq" or "chunk".

    Returns:
        List of SimilarityResult sorted by similarity.
    """
    results: list[SimilarityResult] = []
    compare_fn = (
        compare_chunks if method == "chunk"
        else compare_byte_frequency
    )

    # Group by size range for efficiency
    size_groups: dict[int, list[FileInfo]] = {}
    for fi in files:
        # Group into 10KB buckets
        bucket = fi.size // 10240
        size_groups.setdefault(bucket, []).append(fi)

    for group in size_groups.values():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                sim = compare_fn(group[i].path, group[j].path)
                if sim >= threshold:
                    results.append(
                        SimilarityResult(
                            file_a=group[i].path,
                            file_b=group[j].path,
                            similarity=sim,
                            method=method,
                        )
                    )

    results.sort(key=lambda r: r.similarity, reverse=True)
    return results


def format_similarity_results(
    results: list[SimilarityResult],
) -> str:
    """Format similarity results as text."""
    if not results:
        return "No similar files found."

    lines = [
        f"Similar files: {len(results)} pairs found",
        "",
    ]

    for r in results[:30]:
        lines.append(
            f"  {r.similarity:.0%} similar "
            f"({r.method}): {r.file_a.name} <-> {r.file_b.name}"
        )

    if len(results) > 30:
        lines.append(
            f"\n  ... and {len(results) - 30} more pairs"
        )

    return "\n".join(lines)
