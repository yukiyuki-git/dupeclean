"""File deduplication cleanup validator for DupeClean.

Validate cleanup operations before execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class CleanupValidation:
    """Validation of a cleanup operation."""

    group_id: int
    is_valid: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


@dataclass
class CleanupValidationReport:
    """Complete validation report."""

    groups_checked: int = 0
    groups_valid: int = 0
    groups_invalid: int = 0
    validations: list[CleanupValidation] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.groups_invalid == 0

    @property
    def validity_rate(self) -> float:
        if self.groups_checked == 0:
            return 0.0
        return self.groups_valid / self.groups_checked


def validate_cleanup(group: DuplicateGroup) -> CleanupValidation:
    """Validate a group for cleanup."""
    issues: list[str] = []
    warnings: list[str] = []

    # Check file count
    if len(group.files) < 2:
        issues.append("Group has fewer than 2 files")

    # Check sizes
    sizes = set(f.size for f in group.files)
    if len(sizes) > 1:
        issues.append(f"Inconsistent sizes: {sizes}")

    # Check existence
    for fi in group.files:
        if not fi.path.exists():
            issues.append(f"File not found: {fi.path}")

    # Check for zero-size
    if group.file_size == 0:
        warnings.append("Zero-size files in group")

    return CleanupValidation(
        group_id=group.group_id,
        is_valid=len(issues) == 0,
        issues=issues,
        warnings=warnings,
    )


def validate_cleanup_all(groups: list[DuplicateGroup]) -> CleanupValidationReport:
    """Validate all groups for cleanup."""
    report = CleanupValidationReport(groups_checked=len(groups))
    for group in groups:
        validation = validate_cleanup(group)
        report.validations.append(validation)
        if validation.is_valid:
            report.groups_valid += 1
        else:
            report.groups_invalid += 1
    return report


def format_cleanup_validation(report: CleanupValidationReport) -> str:
    """Format validation report as text."""
    lines = [
        "Cleanup Validation:",
        f"  Groups: {report.groups_checked}",
        f"  Valid: {report.groups_valid}",
        f"  Invalid: {report.groups_invalid}",
        f"  Rate: {report.validity_rate:.1%}",
    ]
    if not report.is_clean:
        lines.append("\n  Issues:")
        for v in report.validations:
            for issue in v.issues:
                lines.append(f"    Group #{v.group_id}: {issue}")
    return "\n".join(lines)
