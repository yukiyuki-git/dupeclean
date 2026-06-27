"""Data models for DupeClean."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SortKey(Enum):
    SIZE = "size"
    NAME = "name"
    COUNT = "count"
    MTIME = "mtime"
    TYPE = "type"


class HashStage(Enum):
    QUICK = "quick"
    MEDIUM = "medium"
    FULL = "full"


class CleanupAction(Enum):
    DELETE = "delete"
    RECYCLE = "recycle"
    HARDLINK = "hardlink"
    MOVE = "move"
    KEEP_NEWEST = "keep_newest"
    KEEP_OLDEST = "keep_oldest"
    KEEP_SHORTEST_PATH = "keep_shortest_path"


@dataclass
class FileInfo:
    """Information about a single file."""

    path: Path
    size: int
    mtime: float
    is_symlink: bool = False
    is_dir: bool = False
    inode: int | None = None
    quick_hash: str | None = None
    medium_hash: str | None = None
    full_hash: str | None = None
    ext: str = ""
    duplicate_group: int | None = None
    marked_for_action: CleanupAction | None = None

    def __post_init__(self) -> None:
        if not self.ext and not self.is_dir:
            self.ext = self.path.suffix.lower()

    @classmethod
    def from_path(cls, path: Path, follow_symlinks: bool = False) -> FileInfo | None:
        try:
            st = path.lstat() if not follow_symlinks else path.stat()
        except (OSError, PermissionError):
            return None
        return cls(
            path=path.resolve() if follow_symlinks else path,
            size=st.st_size,
            mtime=st.st_mtime,
            is_symlink=path.is_symlink(),
            is_dir=path.is_dir(),
            inode=st.st_ino if hasattr(st, "st_ino") else None,
        )

    @property
    def size_display(self) -> str:
        return format_size(self.size)

    @property
    def extension(self) -> str:
        return self.ext.lstrip(".")

    @property
    def hash_for_dedup(self) -> str | None:
        return self.full_hash or self.medium_hash or self.quick_hash


@dataclass
class DirInfo:
    """Aggregated information about a directory."""

    path: Path
    total_size: int = 0
    file_count: int = 0
    dir_count: int = 0
    children: list[DirInfo] = field(default_factory=list)
    files: list[FileInfo] = field(default_factory=list)
    parent: DirInfo | None = None
    depth: int = 0

    @property
    def size_display(self) -> str:
        return format_size(self.total_size)

    @property
    def name(self) -> str:
        return self.path.name or str(self.path)


@dataclass
class DuplicateGroup:
    """A group of files with identical content."""

    group_id: int
    hash_value: str
    file_size: int
    files: list[FileInfo] = field(default_factory=list)
    wasted_space: int = 0

    def __post_init__(self) -> None:
        self.wasted_space = self.file_size * (len(self.files) - 1) if len(self.files) > 1 else 0

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def size_display(self) -> str:
        return format_size(self.file_size)

    @property
    def wasted_display(self) -> str:
        return format_size(self.wasted_space)


@dataclass
class ScanStats:
    """Statistics from a scan operation."""

    total_files: int = 0
    total_dirs: int = 0
    total_size: int = 0
    duplicate_groups: int = 0
    duplicate_files: int = 0
    wasted_space: int = 0
    scan_duration: float = 0.0
    hash_duration: float = 0.0
    largest_file: FileInfo | None = None
    extensions: dict[str, tuple[int, int]] = field(default_factory=dict)

    @property
    def unique_files(self) -> int:
        return self.total_files - self.duplicate_files

    @property
    def dupe_percentage(self) -> float:
        if self.total_size == 0:
            return 0.0
        return (self.wasted_space / self.total_size) * 100


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""

    action: CleanupAction
    files_processed: int = 0
    files_deleted: int = 0
    space_freed: int = 0
    errors: list[str] = field(default_factory=list)
    hardlinks_created: int = 0

    @property
    def space_freed_display(self) -> str:
        return format_size(self.space_freed)


def format_size(size: int, binary: bool = True) -> str:
    """Format bytes into human-readable string."""
    if size < 0:
        return "N/A"
    if size == 0:
        return "0 B"
    units = (
        ["B", "KiB", "MiB", "GiB", "TiB", "PiB"] if binary else ["B", "KB", "MB", "GB", "TB", "PB"]
    )
    base = 1024 if binary else 1000
    for unit in units:
        if abs(size) < base:
            if unit == "B":
                return f"{size} B"
            return f"{size:.1f} {unit}"
        size /= base  # type: ignore[assignment]
    return f"{size:.1f} {units[-1]}"


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"
