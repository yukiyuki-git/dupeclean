"""Multi-stage file hasher for DupeClean."""

from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Optional

from .config import HasherConfig
from .models import FileInfo, HashStage


def _hash_file_chunk(path: Path, size: int, algorithm: str) -> Optional[str]:
    try:
        h = _create_hasher(algorithm)
        bytes_read = 0
        with open(path, "rb") as f:
            while bytes_read < size:
                chunk_size = min(8192, size - bytes_read)
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
                bytes_read += len(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def _hash_file_full(path: Path, algorithm: str) -> Optional[str]:
    try:
        h = _create_hasher(algorithm)
        with open(path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def _create_hasher(algorithm: str):
    if algorithm == "xxhash":
        try:
            import xxhash
            return xxhash.xxh3_128()
        except ImportError:
            pass
    if algorithm in ("md5", "sha256"):
        return hashlib.new(algorithm)
    return hashlib.md5()


class Hasher:
    def __init__(self, config: HasherConfig | None = None) -> None:
        self.config = config or HasherConfig()
        self._cancelled = False
        self._on_progress: Optional[Callable[[str, int, int], None]] = None

    def cancel(self) -> None:
        self._cancelled = True

    def on_progress(self, callback: Callable[[str, int, int], None]) -> None:
        self._on_progress = callback

    def hash_files(self, files: list[FileInfo], stage: HashStage = HashStage.QUICK, threads: int = 4) -> list[FileInfo]:
        self._cancelled = False
        total = len(files)
        completed = 0

        if stage == HashStage.QUICK:
            size = self.config.quick_hash_size
        elif stage == HashStage.MEDIUM:
            size = self.config.medium_hash_size
        else:
            size = 0

        def _hash_one(fi: FileInfo) -> tuple[int, str]:
            if self._cancelled:
                return -1, ""
            path = fi.path
            if stage == HashStage.FULL:
                h = _hash_file_full(path, self.config.algorithm)
            else:
                h = _hash_file_chunk(path, size, self.config.algorithm)
            return id(fi), h or ""

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(_hash_one, fi): fi for fi in files}
            for future in as_completed(futures):
                if self._cancelled:
                    break
                try:
                    file_id, hash_val = future.result()
                    fi = futures[future]
                    if hash_val:
                        if stage == HashStage.QUICK:
                            fi.quick_hash = hash_val
                        elif stage == HashStage.MEDIUM:
                            fi.medium_hash = hash_val
                        else:
                            fi.full_hash = hash_val
                except Exception:
                    pass
                completed += 1
                if completed % 100 == 0 and self._on_progress:
                    self._on_progress(f"Hashing ({stage.value}): {completed}/{total}", completed, total)

        return files
