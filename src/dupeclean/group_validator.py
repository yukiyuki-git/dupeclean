"""File deduplication duplicate group validator for DupeClean.

Validate duplicate groups before cleanup.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class GroupValidation:
    """Validation result for a group."""

    group_id: int
    is_valid: bool
    issues: list[str] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.issues)


@dataclass
class ValidationReport:
    """Complete validation report."""

    groups_checked: int = 0
    groups_valid: int = 0
    groups_invalid: int = 0
    validations: list[GroupValidation] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.groups_invalid == 0

    @property
    def validity_rate(self) -> float:
        if self.groups_checked == 0:
            return 0.0
        return self.groups_valid / self.groups_checked


def validate_group_v2(group: DuplicateGroup) -> GroupValidation:
    """Validate a single duplicate group."""
    issues: list[str] = []

    if len(group.files) < 2:
        issues.append("Group has fewer than 2 files")

    sizes = set(f.size for f in group.files)
    if len(sizes) > 1:
        issues.append(f"Inconsistent sizes: {sizes}")

    for fi in group.files:
        if not fi.path.exists():
            issues.append(f"File not found: {fi.path}")

    return GroupValidation(
        group_id=group.group_id,
        is_valid=len(issues) == 0,
        issues=issues,
    )


def validate_groups_v2(groups: list[DuplicateGroup]) -> ValidationReport:
    """Validate multiple groups."""
    report = ValidationReport(groups_checked=len(groups))

    for group in groups:
        validation = validate_group_v2(group)
        report.validations.append(validation)
        if validation.is_valid:
            report.groups_valid += 1
        else:
            report.groups_invalid += 1

    return report


def format_validation_report_v2(report: ValidationReport) -> str:
    """Format validation report as text."""
    lines = [
        "Validation Report:",
        f"  Groups: {report.groups_checked}",
        f"  Valid: {report.groups_valid}",
        f"  Invalid: {report.groups_invalid}",
        f"  Rate: {report.validity_rate:.1%}",
    ]

    if not report.is_clean:
        lines.append("\n  Issues:")
        for v in report.validations:
            if not v.is_valid:
                for issue in v.issues:
                    lines.append(f"    Group #{v.group_id}: {issue}")

    return "\n".join(lines)
