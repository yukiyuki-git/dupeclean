"""File deduplication file analyzer module for DupeClean.

Analyze individual files for characteristics and metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class FileAnalysis:
    """Analysis of a single file."""

    path: Path
    size: int
    extension: str
    is_empty: bool = False
    is_hidden: bool = False
    is_symlink: bool = False
    is_binary: bool = False
    line_count: int = 0
    char_count: int = 0

    @property
    def size_display(self) -> str:
        return format_size(self.size)


def analyze_file(filepath: Path) -> FileAnalysis | None:
    """Analyze a single file."""
    try:
        stat = filepath.stat()
    except OSError:
        return None

    analysis = FileAnalysis(
        path=filepath,
        size=stat.st_size,
        extension=filepath.suffix.lower(),
        is_empty=stat.st_size == 0,
        is_hidden=filepath.name.startswith("."),
        is_symlink=filepath.is_symlink(),
    )

    # Check if binary
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
        analysis.is_binary = b"\x00" in chunk
    except OSError:
        pass

    # Count lines for text files
    if not analysis.is_binary and not analysis.is_empty:
        try:
            content = filepath.read_text(encoding="utf-8")
            analysis.line_count = content.count("\n") + 1
            analysis.char_count = len(content)
        except (UnicodeDecodeError, OSError):
            pass

    return analysis


def analyze_files(files: list[FileInfo]) -> list[FileAnalysis]:
    """Analyze multiple files."""
    results = []
    for fi in files:
        analysis = analyze_file(fi.path)
        if analysis:
            results.append(analysis)
    return results


def format_file_analysis(analysis: FileAnalysis) -> str:
    """Format file analysis as text."""
    lines = [
        f"File: {analysis.path.name}",
        f"  Size: {analysis.size_display}",
        f"  Extension: {analysis.extension or '(none)'}",
        f"  Binary: {'Yes' if analysis.is_binary else 'No'}",
    ]
    if not analysis.is_binary:
        lines.append(f"  Lines: {analysis.line_count:,}")
    return "\n".join(lines)
