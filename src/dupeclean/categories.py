"""File categorization module for DupeClean.

Automatically categorize files by type and purpose.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import FileInfo, format_size

# Category definitions
CATEGORIES = {
    "documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".odt",
        ".rtf",
        ".tex",
        ".epub",
        ".mobi",
        ".djvu",
    },
    "spreadsheets": {
        ".xls",
        ".xlsx",
        ".ods",
        ".csv",
        ".tsv",
    },
    "presentations": {
        ".ppt",
        ".pptx",
        ".odp",
        ".key",
    },
    "images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".webp",
        ".ico",
        ".tiff",
        ".tif",
        ".raw",
        ".cr2",
        ".nef",
        ".heic",
        ".heif",
    },
    "video": {
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".3gp",
        ".ogv",
    },
    "audio": {
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".wma",
        ".m4a",
        ".opus",
        ".aiff",
    },
    "archives": {
        ".zip",
        ".gz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
        ".tar",
        ".tgz",
        ".lz4",
        ".zst",
    },
    "code": {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".scala",
        ".r",
        ".m",
        ".mm",
        ".lua",
        ".pl",
        ".sh",
        ".bat",
        ".ps1",
        ".sql",
    },
    "markup": {
        ".html",
        ".htm",
        ".xml",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".md",
        ".rst",
        ".tex",
        ".css",
        ".scss",
        ".less",
    },
    "data": {
        ".db",
        ".sqlite",
        ".sqlite3",
        ".mdb",
        ".accdb",
        ".parquet",
        ".feather",
        ".hdf5",
        ".h5",
        ".nc",
    },
    "executables": {
        ".exe",
        ".msi",
        ".dmg",
        ".app",
        ".deb",
        ".rpm",
        ".appimage",
        ".snap",
    },
    "fonts": {
        ".ttf",
        ".otf",
        ".woff",
        ".woff2",
        ".eot",
    },
}


@dataclass
class CategoryInfo:
    """Information about a file category."""

    name: str
    files: list[FileInfo] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def size_display(self) -> str:
        return format_size(self.total_size)


def categorize_file(fi: FileInfo) -> str:
    """Categorize a single file by extension.

    Returns category name or "other".
    """
    ext = fi.ext.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "other"


def categorize_files(
    files: list[FileInfo],
) -> dict[str, CategoryInfo]:
    """Categorize all files.

    Returns dict of category name -> CategoryInfo.
    """
    categories: dict[str, CategoryInfo] = {}

    for fi in files:
        cat = categorize_file(fi)
        if cat not in categories:
            categories[cat] = CategoryInfo(name=cat)
        categories[cat].files.append(fi)

    return categories


def format_categories(
    categories: dict[str, CategoryInfo],
) -> str:
    """Format categories as text."""
    if not categories:
        return "No files to categorize."

    total = sum(c.count for c in categories.values())
    total_size = sum(c.total_size for c in categories.values())

    sorted_cats = sorted(
        categories.items(),
        key=lambda x: x[1].total_size,
        reverse=True,
    )

    lines = [
        f"File Categories: {len(categories)} types, "
        f"{total:,} files, {format_size(total_size)} total",
        "",
    ]

    for name, cat in sorted_cats:
        pct = (cat.total_size / total_size * 100) if total_size else 0
        bar_len = max(1, int(pct / 2.5))
        bar = "█" * bar_len + "░" * (40 - bar_len)
        lines.append(
            f"  {name:<15s} {bar} {cat.size_display:>10s} ({cat.count:>6,} files, {pct:5.1f}%)"
        )

    return "\n".join(lines)
