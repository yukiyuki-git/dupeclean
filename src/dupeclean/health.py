"""Disk health check module for DupeClean.

Comprehensive disk health analysis:
- Filesystem usage patterns
- Error file detection
- Broken symlink detection
- Permission issues
- Hidden space consumers
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HealthIssue:
    """A detected health issue."""
    severity: str  # "info", "warning", "error"
    category: str
    message: str
    path: Path | None = None
    count: int = 0


@dataclass
class HealthReport:
    """Complete disk health report."""
    path: Path
    issues: list[HealthIssue] = field(default_factory=list)
    total_files: int = 0
    total_dirs: int = 0
    broken_symlinks: int = 0
    permission_errors: int = 0
    hidden_files: int = 0
    temp_files: int = 0

    @property
    def error_count(self) -> int:
        return sum(
            1 for i in self.issues if i.severity == "error"
        )

    @property
    def warning_count(self) -> int:
        return sum(
            1 for i in self.issues if i.severity == "warning"
        )

    @property
    def is_healthy(self) -> bool:
        return self.error_count == 0


def check_disk_health(
    path: Path,
    max_depth: int = 5,
) -> HealthReport:
    """Perform a comprehensive disk health check.

    Args:
        path: Root directory to check.
        max_depth: Maximum directory depth to scan.

    Returns:
        HealthReport with all detected issues.
    """
    report = HealthReport(path=path)
    _check_directory(path, 0, max_depth, report)

    # Generate summary issues
    if report.broken_symlinks > 0:
        report.issues.append(
            HealthIssue(
                severity="warning",
                category="symlinks",
                message=f"{report.broken_symlinks} broken symbolic links",
                count=report.broken_symlinks,
            )
        )
    if report.permission_errors > 0:
        report.issues.append(
            HealthIssue(
                severity="warning",
                category="permissions",
                message=f"{report.permission_errors} permission errors",
                count=report.permission_errors,
            )
        )
    if report.temp_files > 10:
        report.issues.append(
            HealthIssue(
                severity="info",
                category="cleanup",
                message=f"{report.temp_files} temporary files found",
                count=report.temp_files,
            )
        )

    return report


def _check_directory(
    directory: Path,
    depth: int,
    max_depth: int,
    report: HealthReport,
) -> None:
    if depth > max_depth:
        return

    try:
        entries = list(os.scandir(directory))
    except PermissionError:
        report.permission_errors += 1
        report.issues.append(
            HealthIssue(
                severity="warning",
                category="permissions",
                message=f"Permission denied: {directory}",
                path=directory,
            )
        )
        return
    except OSError as e:
        report.issues.append(
            HealthIssue(
                severity="error",
                category="filesystem",
                message=f"Error reading {directory}: {e}",
                path=directory,
            )
        )
        return

    for entry in entries:
        path = Path(entry.path)
        name = entry.name

        # Check hidden files
        if name.startswith("."):
            report.hidden_files += 1

        # Check temp files
        if _is_temp_file(name):
            report.temp_files += 1

        try:
            if entry.is_symlink():
                if not path.exists():
                    report.broken_symlinks += 1
                    report.issues.append(
                        HealthIssue(
                            severity="warning",
                            category="symlinks",
                            message=f"Broken symlink: {path}",
                            path=path,
                        )
                    )
            elif entry.is_dir(follow_symlinks=False):
                report.total_dirs += 1
                _check_directory(
                    path, depth + 1, max_depth, report
                )
            elif entry.is_file(follow_symlinks=False):
                report.total_files += 1
        except PermissionError:
            report.permission_errors += 1
        except OSError:
            pass


def _is_temp_file(name: str) -> bool:
    """Check if a filename looks like a temp file."""
    temp_patterns = [
        ".tmp", ".temp", ".bak", ".swp", ".swo",
        "~", ".orig", ".old", ".cache",
    ]
    name_lower = name.lower()
    return any(
        name_lower.endswith(p) or name_lower.startswith(p)
        for p in temp_patterns
    )


def format_health_report(report: HealthReport) -> str:
    """Format a health report as text."""
    lines = [
        f"Disk Health Report: {report.path}",
        f"  Files scanned: {report.total_files:,}",
        f"  Directories: {report.total_dirs:,}",
        "",
    ]

    if report.is_healthy:
        lines.append("  ✅ No critical issues found!")
    else:
        lines.append(
            f"  ❌ {report.error_count} error(s), "
            f"{report.warning_count} warning(s)"
        )

    if report.broken_symlinks:
        lines.append(
            f"  ⚠️  {report.broken_symlinks} broken symlinks"
        )
    if report.permission_errors:
        lines.append(
            f"  🔒 {report.permission_errors} permission errors"
        )
    if report.temp_files:
        lines.append(
            f"  🗑️  {report.temp_files} temp files"
        )
    if report.hidden_files:
        lines.append(
            f"  👁️  {report.hidden_files} hidden files"
        )

    if report.issues:
        lines.append("\n  Issues:")
        for issue in report.issues[:20]:
            icon = {
                "error": "❌",
                "warning": "⚠️",
                "info": "[i]",
            }.get(issue.severity, "?")
            lines.append(f"    {icon} [{issue.category}] {issue.message}")

    return "\n".join(lines)
