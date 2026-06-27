"""File deduplication file validator for DupeClean.

Validate files for integrity and accessibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo, format_size


@dataclass
class ValidationResult:
    """Validation result for a file."""

    path: Path
    is_valid: bool
    issues: list[str] = field(default_factory=list)
    size: int = 0

    @property
    def size_display(self) -> str:
        return format_size(self.size)

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def validate_file(fi: FileInfo) -> ValidationResult:
    """Validate a single file."""
    issues: list[str] = []

    # Check existence
    if not fi.path.exists():
        return ValidationResult(
            path=fi.path,
            is_valid=False,
            issues=["File not found"],
            size=fi.size,
        )

    # Check readability
    try:
        with open(fi.path, "rb") as f:
            f.read(1)
    except PermissionError:
        issues.append("Permission denied")
    except OSError as e:
        issues.append(f"Read error: {e}")

    # Check size consistency
    try:
        actual_size = fi.path.stat().st_size
        if actual_size != fi.size:
            issues.append(f"Size mismatch: expected {fi.size}, got {actual_size}")
    except OSError:
        issues.append("Cannot stat file")

    return ValidationResult(
        path=fi.path,
        is_valid=len(issues) == 0,
        issues=issues,
        size=fi.size,
    )


def validate_files(files: list[FileInfo]) -> list[ValidationResult]:
    """Validate multiple files."""
    return [validate_file(fi) for fi in files]


def format_validation_results(results: list[ValidationResult]) -> str:
    """Format validation results as text."""
    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    invalid = total - valid

    lines = [
        f"Validation: {total} files checked",
        f"  Valid: {valid:,}",
        f"  Invalid: {invalid:,}",
    ]

    if invalid > 0:
        lines.append("\n  Issues:")
        for r in results:
            if not r.is_valid:
                for issue in r.issues:
                    lines.append(f"    {r.path}: {issue}")

    return "\n".join(lines)
