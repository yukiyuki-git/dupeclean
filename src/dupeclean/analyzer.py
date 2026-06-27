"""High-level analysis orchestrator for DupeClean."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from .config import Config
from .dedup import DuplicateFinder, update_scan_stats
from .models import DirInfo, DuplicateGroup, FileInfo, ScanStats, format_duration, format_size
from .scanner import Scanner


class AnalysisResult:
    def __init__(self, root: Path, files: list[FileInfo], dirs: dict[Path, DirInfo], stats: ScanStats, duplicates: list[DuplicateGroup]) -> None:
        self.root = root
        self.files = files
        self.dirs = dirs
        self.stats = stats
        self.duplicates = duplicates

    @property
    def top_extensions(self) -> list[tuple[str, int, int]]:
        items = [(ext, count, size) for ext, (count, size) in self.stats.extensions.items()]
        items.sort(key=lambda x: x[2], reverse=True)
        return items

    @property
    def top_duplicates(self) -> list[DuplicateGroup]:
        return sorted(self.duplicates, key=lambda g: g.wasted_space, reverse=True)

    @property
    def largest_files(self) -> list[FileInfo]:
        return sorted(self.files, key=lambda f: f.size, reverse=True)

    def get_dir_children(self, path: Path) -> list[DirInfo | FileInfo]:
        dir_info = self.dirs.get(path)
        if not dir_info:
            return []
        children: list[DirInfo | FileInfo] = list(dir_info.children)
        children.extend(dir_info.files)
        children.sort(key=lambda x: x.total_size if isinstance(x, DirInfo) else x.size, reverse=True)
        return children

    def summary_text(self) -> str:
        lines = [
            f"Directory: {self.root}",
            f"Total size: {format_size(self.stats.total_size)}",
            f"Files: {self.stats.total_files:,}",
            f"Directories: {self.stats.total_dirs:,}",
            f"Scan time: {format_duration(self.stats.scan_duration)}",
        ]
        if self.duplicates:
            lines.extend([
                "",
                f"Duplicate groups: {self.stats.duplicate_groups:,}",
                f"Duplicate files: {self.stats.duplicate_files:,}",
                f"Wasted space: {format_size(self.stats.wasted_space)} ({self.stats.dupe_percentage:.1f}%)",
            ])
        if self.stats.largest_file:
            lines.extend(["", f"Largest file: {self.stats.largest_file.path}", f"  Size: {self.stats.largest_file.size_display}"])
        top_ext = self.top_extensions[:5]
        if top_ext:
            lines.extend(["", "Top file types:"])
            for ext, count, size in top_ext:
                lines.append(f"  .{ext or '(none)':10s} {count:>8,} files  {format_size(size):>10s}")
        return "\n".join(lines)


class Analyzer:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self._cancelled = False
        self._on_progress: Optional[Callable[[str, int, int], None]] = None

    def cancel(self) -> None:
        self._cancelled = True

    def on_progress(self, callback: Callable[[str, int, int], None]) -> None:
        self._on_progress = callback

    def analyze(self, path: Path, find_dupes: bool = True) -> AnalysisResult:
        self._cancelled = False
        scanner = Scanner(self.config.scanner)
        if self._on_progress:
            scanner.on_progress(lambda msg, count: self._on_progress(msg, count, 0))
        files, dirs, stats = scanner.scan(path)

        duplicates: list[DuplicateGroup] = []
        if find_dupes and not self._cancelled:
            finder = DuplicateFinder(self.config)
            if self._on_progress:
                finder.on_progress(self._on_progress)
            duplicates = finder.find_duplicates(files)
            update_scan_stats(stats, duplicates)

        return AnalysisResult(root=path, files=files, dirs=dirs, stats=stats, duplicates=duplicates)
