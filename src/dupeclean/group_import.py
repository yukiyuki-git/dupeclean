"""File deduplication duplicate group import for DupeClean.

Import duplicate groups from external sources.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, FileInfo


@dataclass
class ImportResult:
    """Result of importing groups."""

    groups: list[DuplicateGroup] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    format: str = ""

    @property
    def count(self) -> int:
        return len(self.groups)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


def import_groups_json(path: Path) -> ImportResult:
    """Import groups from JSON file."""
    result = ImportResult(format="json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data:
            files = [
                FileInfo(path=Path(p), size=entry.get("file_size", 0), mtime=0)
                for p in entry.get("files", [])
            ]
            result.groups.append(
                DuplicateGroup(
                    group_id=entry.get("group_id", 0),
                    hash_value=entry.get("hash", ""),
                    file_size=entry.get("file_size", 0),
                    files=files,
                )
            )
    except (json.JSONDecodeError, OSError, KeyError) as e:
        result.errors.append(str(e))
    return result


def import_groups_csv(path: Path) -> ImportResult:
    """Import groups from CSV file."""
    result = ImportResult(format="csv")
    try:
        content = path.read_text(encoding="utf-8")
        reader = csv.DictReader(io.StringIO(content))
        groups_by_id: dict[int, list[FileInfo]] = {}
        group_hashes: dict[int, str] = {}
        group_sizes: dict[int, int] = {}

        for row in reader:
            group_id = int(row.get("group_id", 0))
            file_path = row.get("file_path", "")
            file_size = int(row.get("file_size", 0))
            hash_val = row.get("hash", "")

            fi = FileInfo(path=Path(file_path), size=file_size, mtime=0)
            groups_by_id.setdefault(group_id, []).append(fi)
            group_hashes[group_id] = hash_val
            group_sizes[group_id] = file_size

        for gid, files in groups_by_id.items():
            result.groups.append(
                DuplicateGroup(
                    group_id=gid,
                    hash_value=group_hashes.get(gid, ""),
                    file_size=group_sizes.get(gid, 0),
                    files=files,
                )
            )
    except (OSError, KeyError, ValueError) as e:
        result.errors.append(str(e))
    return result


def import_groups(path: Path) -> ImportResult:
    """Import groups from file (auto-detect format)."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return import_groups_json(path)
    elif suffix == ".csv":
        return import_groups_csv(path)
    else:
        return ImportResult(errors=[f"Unsupported format: {suffix}"])


def format_import_result(result: ImportResult) -> str:
    """Format import result as text."""
    lines = [
        f"Import: {result.count} groups from {result.format}",
    ]
    if result.has_errors:
        lines.append(f"  Errors: {len(result.errors)}")
        for err in result.errors[:5]:
            lines.append(f"    {err}")
    return "\n".join(lines)
