"""File preview module for DupeClean.

Generate text previews of file contents for quick inspection
without opening files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class FilePreview:
    """Preview of a file's contents."""

    path: Path
    size: int
    preview: str
    truncated: bool = False
    encoding: str = "utf-8"
    is_binary: bool = False

    @property
    def size_display(self) -> str:
        return format_size(self.size)


def preview_file(
    filepath: Path,
    max_lines: int = 20,
    max_chars: int = 2000,
) -> FilePreview | None:
    """Generate a text preview of a file.

    Args:
        filepath: Path to file.
        max_lines: Maximum lines to read.
        max_chars: Maximum characters in preview.

    Returns:
        FilePreview or None if file cannot be read.
    """
    try:
        size = filepath.stat().st_size
    except OSError:
        return None

    # Check if binary
    if _is_likely_binary(filepath):
        return FilePreview(
            path=filepath,
            size=size,
            preview="[Binary file]",
            is_binary=True,
        )

    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = filepath.read_text(encoding="latin-1")
        except OSError:
            return FilePreview(
                path=filepath,
                size=size,
                preview="[Cannot read file]",
                is_binary=True,
            )
    except OSError:
        return None

    lines = content.splitlines()
    truncated = len(lines) > max_lines

    preview_lines = lines[:max_lines]
    preview = "\n".join(preview_lines)

    if len(preview) > max_chars:
        preview = preview[:max_chars]
        truncated = True

    return FilePreview(
        path=filepath,
        size=size,
        preview=preview,
        truncated=truncated,
    )


def _is_likely_binary(filepath: Path) -> bool:
    """Check if a file is likely binary by reading first bytes."""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
        # Check for null bytes (common in binary files)
        return b"\x00" in chunk
    except OSError:
        return False


def format_preview(preview: FilePreview) -> str:
    """Format a file preview as text."""
    lines = [
        f"File: {preview.path}",
        f"Size: {preview.size_display}",
        f"Type: {'Binary' if preview.is_binary else 'Text'}",
        "-" * 60,
        preview.preview,
    ]
    if preview.truncated:
        lines.append("... [truncated]")
    lines.append("-" * 60)
    return "\n".join(lines)


def preview_files(
    files: list[FileInfo],
    max_files: int = 10,
    max_lines: int = 10,
) -> list[FilePreview]:
    """Preview multiple files.

    Args:
        files: Files to preview.
        max_files: Maximum number of files.
        max_lines: Lines per preview.

    Returns:
        List of FilePreview.
    """
    previews: list[FilePreview] = []
    for fi in files[:max_files]:
        preview = preview_file(fi.path, max_lines=max_lines)
        if preview:
            previews.append(preview)
    return previews
