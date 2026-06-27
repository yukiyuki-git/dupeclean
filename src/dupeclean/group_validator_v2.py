"""File deduplication group validator v2 for DupeClean.

Enhanced validation with more checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class ValidationCheck:
    """A single validation check."""

    check_name: str
    passed: bool
    message: str = ""


@dataclass
class GroupValidationV2:
    """Enhanced validation for a group."""

    group_id: int
    checks: list[ValidationCheck] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failed_checks(self) -> list[ValidationCheck]:
        return [c for c in self.checks if not c.passed]


@dataclass
class ValidationReportV2:
    """Complete validation report."""

    groups_checked: int = 0
    groups_valid: int = 0
    groups_invalid: int = 0
    validations: list[GroupValidationV2] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.groups_invalid == 0

    @property
    def validity_rate(self) -> float:
        if self.groups_checked == 0:
            return 0.0
        return self.groups_valid / self.groups_checked


def validate_group_v2(group: DuplicateGroup) -> GroupValidationV2:
    """Validate a group with multiple checks."""
    validation = GroupValidationV2(group_id=group.group_id)

    # Check file count
    validation.checks.append(
        ValidationCheck(
            check_name="file_count",
            passed=len(group.files) >= 2,
            message=f"{len(group.files)} files" if len(group.files) >= 2 else "Too few files",
        )
    )

    # Check size consistency
    sizes = set(f.size for f in group.files)
    validation.checks.append(
        ValidationCheck(
            check_name="size_consistency",
            passed=len(sizes) <= 1,
            message=f"Sizes: {sizes}" if len(sizes) > 1 else "Consistent",
        )
    )

    # Check file existence
    all_exist = all(f.path.exists() for f in group.files)
    validation.checks.append(
        ValidationCheck(
            check_name="files_exist",
            passed=all_exist,
            message="All exist" if all_exist else "Some missing",
        )
    )

    # Check zero-size files
    has_zero = any(f.size == 0 for f in group.files)
    validation.checks.append(
        ValidationCheck(
            check_name="non_zero_size",
            passed=not has_zero,
            message="All non-zero" if not has_zero else "Contains zero-size files",
        )
    )

    return validation


def validate_groups_v2(groups: list[DuplicateGroup]) -> ValidationReportV2:
    """Validate multiple groups."""
    report = ValidationReportV2(groups_checked=len(groups))

    for group in groups:
        validation = validate_group_v2(group)
        report.validations.append(validation)
        if validation.is_valid:
            report.groups_valid += 1
        else:
            report.groups_invalid += 1

    return report


def format_validation_v2(report: ValidationReportV2) -> str:
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
            for check in v.failed_checks:
                lines.append(f"    Group #{v.group_id}: {check.check_name} - {check.message}")

    return "\n".join(lines)
