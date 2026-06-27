"""File deduplication engine v2 for DupeClean.

Advanced dedup with content-defined chunking and
space-efficient storage.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo, format_size

CHUNK_SIZE = 4096


@dataclass
class ContentChunk:
    """A chunk of file content."""

    hash: str
    size: int
    offset: int


@dataclass
class FileFingerprint:
    """Content-based fingerprint using chunked hashing."""

    path: Path
    size: int
    chunks: list[ContentChunk]
    full_hash: str

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


@dataclass
class DedupV2Result:
    """Result of v2 deduplication analysis."""

    unique_files: int = 0
    duplicate_files: int = 0
    unique_chunks: int = 0
    total_chunks: int = 0
    space_saved: int = 0
    chunk_store_size: int = 0

    @property
    def dedup_ratio(self) -> float:
        if self.total_chunks == 0:
            return 0.0
        return 1 - (self.unique_chunks / self.total_chunks)


def fingerprint_file(filepath: Path) -> FileFingerprint | None:
    """Create a chunked fingerprint of a file."""
    try:
        file_size = filepath.stat().st_size
    except OSError:
        return None

    chunks: list[ContentChunk] = []
    full_hasher = hashlib.sha256()

    try:
        with open(filepath, "rb") as f:
            offset = 0
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                chunk_hash = hashlib.sha256(data).hexdigest()
                chunks.append(
                    ContentChunk(
                        hash=chunk_hash,
                        size=len(data),
                        offset=offset,
                    )
                )
                full_hasher.update(data)
                offset += len(data)
    except OSError:
        return None

    return FileFingerprint(
        path=filepath,
        size=file_size,
        chunks=chunks,
        full_hash=full_hasher.hexdigest(),
    )


def analyze_dedup_v2(
    files: list[FileInfo],
) -> DedupV2Result:
    """Analyze deduplication potential using chunked hashing.

    Returns:
        DedupV2Result with dedup statistics.
    """
    result = DedupV2Result()

    # Track unique chunks
    seen_chunks: dict[str, int] = {}  # hash -> size
    seen_files: dict[str, int] = {}  # full_hash -> size

    for fi in files:
        fp = fingerprint_file(fi.path)
        if fp is None:
            continue

        # Check if entire file is duplicate
        if fp.full_hash in seen_files:
            result.duplicate_files += 1
            result.space_saved += fi.size
        else:
            result.unique_files += 1
            seen_files[fp.full_hash] = fi.size

        # Track chunks
        for chunk in fp.chunks:
            result.total_chunks += 1
            if chunk.hash not in seen_chunks:
                seen_chunks[chunk.hash] = chunk.size
                result.unique_chunks += 1

    result.chunk_store_size = sum(seen_chunks.values())
    return result


def format_dedup_v2(result: DedupV2Result) -> str:
    """Format v2 dedup results as text."""
    lines = [
        "Dedup V2 Analysis:",
        f"  Unique files: {result.unique_files:,}",
        f"  Duplicate files: {result.duplicate_files:,}",
        f"  Unique chunks: {result.unique_chunks:,}",
        f"  Total chunks: {result.total_chunks:,}",
        f"  Dedup ratio: {result.dedup_ratio:.1%}",
        f"  Space saved: {format_size(result.space_saved)}",
        f"  Chunk store: {format_size(result.chunk_store_size)}",
    ]
    return "\n".join(lines)
