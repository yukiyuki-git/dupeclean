"""Utility functions for DupeClean."""

from __future__ import annotations

import fnmatch
import os
import sys
from pathlib import Path
from typing import Optional


def is_hidden(path: Path) -> bool:
    name = path.name
    if name in (".", ".."):
        return False
    if name.startswith("."):
        return True
    if sys.platform == "win32":
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            return bool(attrs & 2)
        except (AttributeError, OSError):
            return False
    return False


def matches_pattern(name: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def safe_stat(path: Path, follow_symlinks: bool = False) -> Optional[os.stat_result]:
    try:
        return path.stat() if follow_symlinks else path.lstat()
    except (OSError, PermissionError):
        return None


def is_same_file(path1: Path, path2: Path) -> bool:
    try:
        st1 = path1.stat()
        st2 = path2.stat()
        return st1.st_dev == st2.st_dev and st1.st_ino == st2.st_ino
    except (OSError, PermissionError):
        return False


def get_file_extension(path: Path) -> str:
    ext = path.suffix.lower()
    return ext.lstrip(".")


def truncate_path(path: str, max_len: int = 60) -> str:
    if len(path) <= max_len:
        return path
    parts = path.split(os.sep)
    if len(parts) <= 3:
        return path
    return os.sep.join([parts[0], "...", parts[-2], parts[-1]])


def get_terminal_size() -> tuple[int, int]:
    try:
        columns, lines = os.get_terminal_size()
        return columns, lines
    except (OSError, ValueError):
        return 80, 24


def human_count(n: int) -> str:
    return f"{n:,}"


def safe_remove(path: Path) -> tuple[bool, str]:
    try:
        if path.is_dir():
            return False, f"Is a directory: {path}"
        path.unlink()
        return True, ""
    except PermissionError:
        return False, f"Permission denied: {path}"
    except FileNotFoundError:
        return True, ""
    except OSError as e:
        return False, f"Error removing {path}: {e}"


def safe_rmdir(path: Path) -> tuple[bool, str]:
    try:
        path.rmdir()
        return True, ""
    except OSError:
        return False, ""


def create_hardlink(source: Path, target: Path) -> tuple[bool, str]:
    try:
        if target.exists():
            target.unlink()
        target.hardlink_to(source)
        return True, ""
    except OSError as e:
        return False, f"Failed to create hardlink: {e}"


class ProgressCallback:
    def __init__(self, total: int = 0) -> None:
        self.total = total
        self.current = 0
        self.message = ""

    def update(self, increment: int = 1, message: str = "") -> None:
        self.current += increment
        if message:
            self.message = message

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100)

    @property
    def fraction(self) -> str:
        return f"{self.current}/{self.total}"
