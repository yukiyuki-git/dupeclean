"""File validation module for DupeClean.

Validate file integrity and detect corruption.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileInfo


@dataclass
class ValidationResult:
    """Result of file validation."""

    path: Path
    is_valid: bool
    issues: list[str] = field(default_factory=list)
    size: int = 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


@dataclass
class ValidationReport:
    """Complete validation report."""

    total_files: int = 0
    valid_files: int = 0
    invalid_files: int = 0
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.invalid_files == 0

    @property
    def error_rate(self) -> float:
        if self.total_files == 0:
            return 0.0
        return self.invalid_files / self.total_files


def validate_file(filepath: Path) -> ValidationResult:
    """Validate a single file.

    Checks:
    - File exists and is readable
    - Size matches stat
    - No read errors
    """
    issues: list[str] = []
    size = 0

    # Check existence
    if not filepath.exists():
        return ValidationResult(path=filepath, is_valid=False, issues=["File not found"])

    # Check if readable
    try:
        stat = filepath.stat()
        size = stat.st_size
    except OSError as e:
        return ValidationResult(
            path=filepath,
            is_valid=False,
            issues=[f"Cannot stat: {e}"],
        )

    # Try reading
    try:
        with open(filepath, "rb") as f:
            data = f.read()
            if len(data) != size:
                issues.append(f"Size mismatch: stat={size}, read={len(data)}")
    except OSError as e:
        issues.append(f"Read error: {e}")

    return ValidationResult(
        path=filepath,
        is_valid=len(issues) == 0,
        issues=issues,
        size=size,
    )


def validate_files(
    files: list[FileInfo],
) -> ValidationReport:
    """Validate multiple files.

    Returns:
        ValidationReport with all results.
    """
    report = ValidationReport(total_files=len(files))

    for fi in files:
        result = validate_file(fi.path)
        report.results.append(result)
        if result.is_valid:
            report.valid_files += 1
        else:
            report.invalid_files += 1

    return report


def check_file_integrity(filepath: Path, expected_hash: str, algorithm: str = "sha256") -> bool:
    """Check if a file matches an expected hash.

    Args:
        filepath: Path to file.
        expected_hash: Expected hex digest.
        algorithm: Hash algorithm.

    Returns:
        True if hash matches.
    """
    try:
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest() == expected_hash
    except OSError:
        return False


def format_validation_report(report: ValidationReport) -> str:
    """Format validation report as text."""
    lines = [
        "Validation Report:",
        f"  Total files: {report.total_files:,}",
        f"  Valid: {report.valid_files:,}",
        f"  Invalid: {report.invalid_files:,}",
    ]

    if report.is_clean:
        lines.append("  Status: All files valid!")
    else:
        lines.append(f"  Error rate: {report.error_rate:.1%}")
        lines.append("\n  Issues:")
        for result in report.results:
            if not result.is_valid:
                for issue in result.issues:
                    lines.append(f"    {result.path}: {issue}")

    return "\n".join(lines)
