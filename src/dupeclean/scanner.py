"""File system scanner for DupeClean."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from pathlib import Path

from .config import ScannerConfig
from .models import DirInfo, FileInfo, ScanStats
from .utils import is_hidden, matches_pattern


class Scanner:
    def __init__(self, config: ScannerConfig | None = None) -> None:
        self.config = config or ScannerConfig()
        self._cancelled = False
        self._stats = ScanStats()
        self._files: list[FileInfo] = []
        self._dirs: dict[Path, DirInfo] = {}
        self._on_progress: Callable[[str, int], None] | None = None

    def cancel(self) -> None:
        self._cancelled = True

    def on_progress(self, callback: Callable[[str, int], None]) -> None:
        self._on_progress = callback

    def _report_progress(self, message: str, count: int) -> None:
        if self._on_progress:
            self._on_progress(message, count)

    def scan(self, root: Path) -> tuple[list[FileInfo], dict[Path, DirInfo], ScanStats]:
        self._cancelled = False
        self._files = []
        self._dirs = {}
        self._stats = ScanStats()
        start = time.monotonic()
        root = root.resolve()

        if not root.exists():
            raise FileNotFoundError(f"Path not found: {root}")

        if root.is_file():
            fi = FileInfo.from_path(root, self.config.follow_symlinks)
            if fi:
                self._files.append(fi)
                self._stats.total_files = 1
                self._stats.total_size = fi.size
                self._stats.largest_file = fi
            self._stats.scan_duration = time.monotonic() - start
            return self._files, self._dirs, self._stats

        self._walk(root, depth=0, parent=None)
        self._stats.scan_duration = time.monotonic() - start
        return self._files, self._dirs, self._stats

    def _walk(self, directory: Path, depth: int, parent: DirInfo | None) -> None:
        if self._cancelled:
            return

        dir_info = DirInfo(path=directory, depth=depth, parent=parent)
        self._dirs[directory] = dir_info

        try:
            entries = list(os.scandir(directory))
        except (PermissionError, OSError):
            return

        subdirs: list[Path] = []

        for entry in entries:
            if self._cancelled:
                return
            try:
                path = Path(entry.path)
                name = entry.name
                if matches_pattern(name, self.config.ignore_patterns):
                    continue
                if self.config.skip_hidden and is_hidden(path):
                    continue
                if entry.is_symlink() and not self.config.follow_symlinks:
                    self._stats.total_files += 1
                    continue
                if entry.is_dir(follow_symlinks=self.config.follow_symlinks):
                    self._stats.total_dirs += 1
                    subdirs.append(path)
                elif entry.is_file(follow_symlinks=self.config.follow_symlinks):
                    fi = FileInfo.from_path(path, self.config.follow_symlinks)
                    if fi:
                        self._files.append(fi)
                        dir_info.files.append(fi)
                        dir_info.total_size += fi.size
                        dir_info.file_count += 1
                        self._stats.total_files += 1
                        self._stats.total_size += fi.size
                        if (
                            self._stats.largest_file is None
                            or fi.size > self._stats.largest_file.size
                        ):
                            self._stats.largest_file = fi
                        ext = fi.extension or "(no ext)"
                        if ext not in self._stats.extensions:
                            self._stats.extensions[ext] = (0, 0)
                        count, size = self._stats.extensions[ext]
                        self._stats.extensions[ext] = (count + 1, size + fi.size)
                        if self._stats.total_files % 1000 == 0:
                            self._report_progress(
                                f"Scanned {self._stats.total_files:,} files...",
                                self._stats.total_files,
                            )
            except (PermissionError, OSError):
                continue

        for subdir in subdirs:
            if self._cancelled:
                return
            self._walk(subdir, depth + 1, dir_info)
            child = self._dirs.get(subdir)
            if child:
                dir_info.total_size += child.total_size
                dir_info.file_count += child.file_count
                dir_info.dir_count += 1 + child.dir_count
                dir_info.children.append(child)

    def get_sorted_children(self, dir_path: Path) -> list[DirInfo | FileInfo]:
        dir_info = self._dirs.get(dir_path)
        if not dir_info:
            return []
        children: list[DirInfo | FileInfo] = list(dir_info.children)
        children.extend(dir_info.files)
        children.sort(
            key=lambda x: x.total_size if isinstance(x, DirInfo) else x.size,
            reverse=True,
        )
        return children
