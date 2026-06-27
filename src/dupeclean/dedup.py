"""Duplicate detection engine for DupeClean."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable, Optional

from .config import Config
from .hasher import Hasher
from .models import DuplicateGroup, FileInfo, HashStage, ScanStats


class DuplicateFinder:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self.hasher = Hasher(self.config.hasher)
        self._cancelled = False
        self._on_progress: Optional[Callable[[str, int, int], None]] = None

    def cancel(self) -> None:
        self._cancelled = True
        self.hasher.cancel()

    def on_progress(self, callback: Callable[[str, int, int], None]) -> None:
        self._on_progress = callback

    def find_duplicates(self, files: list[FileInfo]) -> list[DuplicateGroup]:
        self._cancelled = False
        start = time.monotonic()

        if self._on_progress:
            self._on_progress("Grouping by size...", 0, 0)

        # Stage 1: Group by size
        size_groups = self._group_by_size(files)
        candidates = self._get_size_candidates(size_groups)

        if not candidates:
            return []

        if self._on_progress:
            self._on_progress(f"Found {len(candidates)} files with same-size siblings", 0, len(candidates))

        # Stage 2: Quick hash
        if self._cancelled:
            return []
        self.hasher.hash_files(candidates, HashStage.QUICK, self.config.scanner.threads)
        quick_groups = self._group_by_hash(candidates, "quick_hash")
        candidates = self._get_hash_candidates(quick_groups)

        if not candidates:
            return []

        # Stage 3: Medium hash
        if self._cancelled:
            return []
        self.hasher.hash_files(candidates, HashStage.MEDIUM, self.config.scanner.threads)
        medium_groups = self._group_by_hash(candidates, "medium_hash")
        candidates = self._get_hash_candidates(medium_groups)

        if not candidates:
            return []

        # Stage 4: Full hash
        if self._cancelled:
            return []
        self.hasher.hash_files(candidates, HashStage.FULL, self.config.scanner.threads)
        full_groups = self._group_by_hash(candidates, "full_hash")

        groups = []
        group_id = 0
        for hash_val, group_files in full_groups.items():
            if len(group_files) < 2:
                continue
            group = DuplicateGroup(group_id=group_id, hash_value=hash_val, file_size=group_files[0].size, files=group_files)
            for fi in group_files:
                fi.duplicate_group = group_id
            groups.append(group)
            group_id += 1

        groups.sort(key=lambda g: g.wasted_space, reverse=True)
        return groups

    def _group_by_size(self, files: list[FileInfo]) -> dict[int, list[FileInfo]]:
        groups: dict[int, list[FileInfo]] = defaultdict(list)
        for fi in files:
            if fi.size > 0:
                groups[fi.size].append(fi)
        return {size: group for size, group in groups.items() if len(group) >= 2}

    def _get_size_candidates(self, groups: dict[int, list[FileInfo]]) -> list[FileInfo]:
        candidates = []
        for group in groups.values():
            candidates.extend(group)
        return candidates

    def _group_by_hash(self, files: list[FileInfo], hash_attr: str) -> dict[str, list[FileInfo]]:
        groups: dict[str, list[FileInfo]] = defaultdict(list)
        for fi in files:
            h = getattr(fi, hash_attr, None)
            if h:
                groups[h].append(fi)
        return {h: g for h, g in groups.items() if len(g) >= 2}

    def _get_hash_candidates(self, groups: dict[str, list[FileInfo]]) -> list[FileInfo]:
        candidates = []
        for group in groups.values():
            candidates.extend(group)
        return candidates


def quick_find_duplicates(files: list[FileInfo], config: Config | None = None) -> list[DuplicateGroup]:
    finder = DuplicateFinder(config)
    return finder.find_duplicates(files)


def update_scan_stats(stats: ScanStats, groups: list[DuplicateGroup]) -> ScanStats:
    stats.duplicate_groups = len(groups)
    stats.duplicate_files = sum(g.count for g in groups)
    stats.wasted_space = sum(g.wasted_space for g in groups)
    return stats
