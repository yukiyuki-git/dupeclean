"""File deduplication file categorizer module for DupeClean.

Categorize files by type, purpose, and characteristics.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import FileInfo, format_size


@dataclass
class Category:
    """A file category."""
    name: str
    description: str
    files: list[FileInfo] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def size_display(self) -> str:
        return format_size(self.total_size)


# Built-in categories
CATEGORIES = {
    "documents": Category(
        name="Documents",
        description="Text documents and PDFs",
        extensions=[".pdf", ".doc", ".docx", ".odt", ".txt", ".rtf"],
    ),
    "images": Category(
        name="Images",
        description="Image files",
        extensions=[".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    ),
    "videos": Category(
        name="Videos",
        description="Video files",
        extensions=[".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm"],
    ),
    "audio": Category(
        name="Audio",
        description="Audio files",
        extensions=[".mp3", ".wav", ".flac", ".ogg", ".aac", ".wma"],
    ),
    "code": Category(
        name="Code",
        description="Source code files",
        extensions=[".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs", ".rb"],
    ),
    "archives": Category(
        name="Archives",
        description="Compressed archives",
        extensions=[".zip", ".gz", ".tar", ".rar", ".7z", ".bz2"],
    ),
    "data": Category(
        name="Data",
        description="Data files",
        extensions=[".json", ".csv", ".xml", ".yaml", ".yml", ".toml"],
    ),
}


def categorize_file(fi: FileInfo) -> str:
    """Categorize a single file."""
    ext = fi.ext.lower()
    for name, cat in CATEGORIES.items():
        if ext in cat.extensions:
            return name
    return "other"


def categorize_files(files: list[FileInfo]) -> dict[str, Category]:
    """Categorize all files."""
    result: dict[str, Category] = {}
    for name, cat in CATEGORIES.items():
        result[name] = Category(
            name=cat.name,
            description=cat.description,
            extensions=cat.extensions,
        )
    result["other"] = Category(name="Other", description="Uncategorized files")

    for fi in files:
        cat_name = categorize_file(fi)
        result[cat_name].files.append(fi)

    return {k: v for k, v in result.items() if v.count > 0}


def format_categories(categories: dict[str, Category]) -> str:
    """Format categories as text."""
    total = sum(c.count for c in categories.values())
    total_size = sum(c.total_size for c in categories.values())

    lines = [
        f"File Categories: {len(categories)} types, "
        f"{total:,} files, {format_size(total_size)}",
        "",
    ]

    for _name, cat in sorted(
        categories.items(), key=lambda x: x[1].total_size, reverse=True
    ):
        pct = (cat.total_size / total_size * 100) if total_size > 0 else 0
        lines.append(
            f"  {cat.name:<15s} {cat.count:>6,} files  "
            f"{cat.size_display:>10s} ({pct:5.1f}%)"
        )

    return "\n".join(lines)
