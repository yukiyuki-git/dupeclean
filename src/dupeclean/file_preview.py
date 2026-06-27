"""File deduplication file preview for DupeClean.

Preview file contents without opening them.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class FilePreviewData:
    """Preview data for a file."""

    path: Path
    size: int
    preview: str
    is_binary: bool = False
    truncated: bool = False
    encoding: str = "utf-8"

    @property
    def size_display(self) -> str:
        return format_size(self.size)


def preview_file_content(
    filepath: Path,
    max_lines: int = 20,
    max_chars: int = 2000,
) -> FilePreviewData | None:
    """Preview a file's contents."""
    try:
        size = filepath.stat().st_size
    except OSError:
        return None

    # Check if binary
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return FilePreviewData(
                path=filepath,
                size=size,
                preview="[Binary file]",
                is_binary=True,
            )
    except OSError:
        return None

    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = filepath.read_text(encoding="latin-1")
        except OSError:
            return FilePreviewData(
                path=filepath,
                size=size,
                preview="[Cannot read file]",
                is_binary=True,
            )
    except OSError:
        return None

    lines = content.splitlines()
    truncated = len(lines) > max_lines
    preview = "\n".join(lines[:max_lines])

    if len(preview) > max_chars:
        preview = preview[:max_chars]
        truncated = True

    return FilePreviewData(
        path=filepath,
        size=size,
        preview=preview,
        truncated=truncated,
    )


def format_preview_data(preview: FilePreviewData) -> str:
    """Format preview data as text."""
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


def preview_multiple(
    files: list[FileInfo],
    max_files: int = 10,
    max_lines: int = 10,
) -> list[FilePreviewData]:
    """Preview multiple files."""
    previews: list[FilePreviewData] = []
    for fi in files[:max_files]:
        preview = preview_file_content(fi.path, max_lines=max_lines)
        if preview:
            previews.append(preview)
    return previews
