"""File export module for DupeClean.

Export scan results in various formats for external tools.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from .analyzer import AnalysisResult
from .models import format_size


def export_json(result: AnalysisResult, path: Path) -> None:
    """Export full analysis as JSON."""
    data = _build_export_data(result)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def export_csv(result: AnalysisResult, path: Path) -> None:
    """Export files as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "path",
            "size",
            "extension",
            "mtime",
            "is_symlink",
        ]
    )
    for fi in result.files:
        writer.writerow(
            [
                str(fi.path),
                fi.size,
                fi.ext,
                fi.mtime,
                fi.is_symlink,
            ]
        )
    path.write_text(output.getvalue(), encoding="utf-8")


def export_tsv(result: AnalysisResult, path: Path) -> None:
    """Export files as TSV."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t")
    writer.writerow(["path", "size", "extension"])
    for fi in result.files:
        writer.writerow([str(fi.path), fi.size, fi.ext])
    path.write_text(output.getvalue(), encoding="utf-8")


def export_html_report(result: AnalysisResult, path: Path) -> None:
    """Export as standalone HTML report."""
    from .report import ReportGenerator

    gen = ReportGenerator(result)
    content = gen.generate("html")
    if content:
        path.write_text(content, encoding="utf-8")


def export_summary(result: AnalysisResult, path: Path) -> None:
    """Export as plain text summary."""
    path.write_text(result.summary_text(), encoding="utf-8")


def _build_export_data(result: AnalysisResult) -> dict:
    """Build export data structure."""
    return {
        "metadata": {
            "version": "1.0",
            "tool": "DupeClean",
            "root": str(result.root),
        },
        "summary": {
            "total_files": result.stats.total_files,
            "total_dirs": result.stats.total_dirs,
            "total_size": result.stats.total_size,
            "total_size_display": format_size(result.stats.total_size),
            "duplicate_groups": result.stats.duplicate_groups,
            "duplicate_files": result.stats.duplicate_files,
            "wasted_space": result.stats.wasted_space,
            "scan_duration": result.stats.scan_duration,
        },
        "files": [
            {
                "path": str(f.path),
                "size": f.size,
                "extension": f.ext,
                "mtime": f.mtime,
            }
            for f in result.files
        ],
        "duplicates": [
            {
                "group_id": g.group_id,
                "hash": g.hash_value,
                "file_size": g.file_size,
                "wasted_space": g.wasted_space,
                "files": [str(f.path) for f in g.files],
            }
            for g in result.duplicates
        ],
        "extensions": [
            {"ext": ext, "count": count, "size": size} for ext, count, size in result.top_extensions
        ],
    }
