"""File deduplication storage module for DupeClean.

Content-addressable storage for space-efficient dedup.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size


@dataclass
class StorageStats:
    """Storage statistics."""

    total_files: int = 0
    unique_chunks: int = 0
    total_chunks: int = 0
    dedup_ratio: float = 0.0
    storage_saved: int = 0

    @property
    def saved_display(self) -> str:
        return format_size(self.storage_saved)


@dataclass
class ContentRef:
    """A reference to stored content."""

    hash: str
    size: int
    ref_count: int = 1


@dataclass
class CAS:
    """Content-Addressable Storage for deduplication."""

    chunks: dict[str, ContentRef] = field(default_factory=dict)

    def store(self, data: bytes) -> str:
        """Store content and return its hash."""
        h = hashlib.sha256(data).hexdigest()
        if h in self.chunks:
            self.chunks[h].ref_count += 1
        else:
            self.chunks[h] = ContentRef(hash=h, size=len(data))
        return h

    def retrieve(self, content_hash: str) -> ContentRef | None:
        """Get content reference by hash."""
        return self.chunks.get(content_hash)

    def exists(self, content_hash: str) -> bool:
        """Check if content exists in storage."""
        return content_hash in self.chunks

    def stats(self) -> StorageStats:
        """Get storage statistics."""
        total_refs = sum(c.ref_count for c in self.chunks.values())
        unique = len(self.chunks)
        saved = sum(c.size * (c.ref_count - 1) for c in self.chunks.values() if c.ref_count > 1)
        ratio = 1 - (unique / total_refs) if total_refs > 0 else 0
        return StorageStats(
            total_files=total_refs,
            unique_chunks=unique,
            total_chunks=total_refs,
            dedup_ratio=ratio,
            storage_saved=saved,
        )

    def add_file(self, filepath: Path) -> str | None:
        """Add a file to storage."""
        try:
            data = filepath.read_bytes()
            return self.store(data)
        except OSError:
            return None

    def add_file_chunks(self, filepath: Path, chunk_size: int = 4096) -> list[str]:
        """Add a file in chunks."""
        hashes: list[str] = []
        try:
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h = self.store(chunk)
                    hashes.append(h)
        except OSError:
            pass
        return hashes

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def total_size(self) -> int:
        return sum(c.size for c in self.chunks.values())

    @property
    def total_size_display(self) -> str:
        return format_size(self.total_size)


def format_cas_stats(cas: CAS) -> str:
    """Format CAS statistics as text."""
    stats = cas.stats()
    lines = [
        "Content-Addressable Storage:",
        f"  Unique chunks: {stats.unique_chunks:,}",
        f"  Total references: {stats.total_chunks:,}",
        f"  Dedup ratio: {stats.dedup_ratio:.1%}",
        f"  Storage saved: {stats.saved_display}",
        f"  Storage size: {cas.total_size_display}",
    ]
    return "\n".join(lines)
