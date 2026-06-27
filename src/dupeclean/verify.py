"""File deduplication verification module for DupeClean.

Verify that dedup operations were successful and didn't
corrupt any files.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size


@dataclass
class VerificationResult:
    """Result of verifying a dedup operation."""

    path: Path
    expected_hash: str
    actual_hash: str
    is_valid: bool
    size: int = 0
    error: str = ""

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class VerificationReport:
    """Complete verification report."""

    total_checked: int = 0
    total_valid: int = 0
    total_invalid: int = 0
    total_errors: int = 0
    results: list[VerificationResult] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.total_invalid == 0 and self.total_errors == 0

    @property
    def success_rate(self) -> float:
        if self.total_checked == 0:
            return 0.0
        return self.total_valid / self.total_checked


def verify_file(filepath: Path, expected_hash: str) -> VerificationResult:
    """Verify a single file against expected hash."""
    try:
        size = filepath.stat().st_size
    except OSError as e:
        return VerificationResult(
            path=filepath,
            expected_hash=expected_hash,
            actual_hash="",
            is_valid=False,
            error=str(e),
        )

    try:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        actual = h.hexdigest()
        return VerificationResult(
            path=filepath,
            expected_hash=expected_hash,
            actual_hash=actual,
            is_valid=actual == expected_hash,
            size=size,
        )
    except OSError as e:
        return VerificationResult(
            path=filepath,
            expected_hash=expected_hash,
            actual_hash="",
            is_valid=False,
            size=size,
            error=str(e),
        )


def verify_files(
    files: dict[Path, str],
) -> VerificationReport:
    """Verify multiple files against their expected hashes.

    Args:
        files: Dict of filepath -> expected_hash.

    Returns:
        VerificationReport with all results.
    """
    report = VerificationReport()

    for filepath, expected_hash in files.items():
        result = verify_file(filepath, expected_hash)
        report.results.append(result)
        report.total_checked += 1

        if result.error:
            report.total_errors += 1
        elif result.is_valid:
            report.total_valid += 1
        else:
            report.total_invalid += 1

    return report


def format_verification_report(
    report: VerificationReport,
) -> str:
    """Format verification report as text."""
    lines = [
        "Verification Report:",
        f"  Checked: {report.total_checked:,}",
        f"  Valid: {report.total_valid:,}",
        f"  Invalid: {report.total_invalid:,}",
        f"  Errors: {report.total_errors:,}",
        f"  Success rate: {report.success_rate:.1%}",
    ]

    if report.is_clean:
        lines.append("  Status: All files verified OK!")
    else:
        lines.append("\n  Issues:")
        for r in report.results:
            if not r.is_valid:
                lines.append(f"    {r.path}: {r.error or 'Hash mismatch'}")

    return "\n".join(lines)
