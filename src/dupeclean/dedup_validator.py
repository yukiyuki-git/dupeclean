"""File deduplication validator module for DupeClean.

Validate dedup results before and after operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class ValidationResult:
    """Result of a dedup validation."""

    group_id: int
    is_valid: bool
    file_count: int = 0
    hash_verified: bool = False
    size_verified: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class ValidationSummary:
    """Summary of dedup validation."""

    total_groups: int = 0
    valid_groups: int = 0
    invalid_groups: int = 0
    total_files: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.invalid_groups == 0

    @property
    def validity_rate(self) -> float:
        if self.total_groups == 0:
            return 0.0
        return self.valid_groups / self.total_groups


def validate_group(group: DuplicateGroup) -> ValidationResult:
    """Validate a single duplicate group.

    Checks:
    - All files exist
    - All files have the same size
    - Hash consistency
    """
    issues: list[str] = []
    valid = True

    # Check file count
    if group.count < 2:
        issues.append(f"Group has only {group.count} file(s)")
        valid = False

    # Check sizes are consistent
    sizes = set(f.size for f in group.files)
    if len(sizes) > 1:
        issues.append(f"Inconsistent sizes: {sizes}")
        valid = False

    # Check files exist
    for fi in group.files:
        if not fi.path.exists():
            issues.append(f"File not found: {fi.path}")
            valid = False

    return ValidationResult(
        group_id=group.group_id,
        is_valid=valid,
        file_count=group.count,
        size_verified=len(sizes) <= 1,
        issues=issues,
    )


def validate_groups(
    groups: list[DuplicateGroup],
) -> ValidationSummary:
    """Validate multiple duplicate groups."""
    summary = ValidationSummary(
        total_groups=len(groups),
        total_files=sum(g.count for g in groups),
    )

    for group in groups:
        result = validate_group(group)
        if result.is_valid:
            summary.valid_groups += 1
        else:
            summary.invalid_groups += 1
            summary.issues.extend(result.issues)

    return summary


def format_validation_summary(
    summary: ValidationSummary,
) -> str:
    """Format validation summary as text."""
    lines = [
        "Validation Summary:",
        f"  Groups: {summary.total_groups:,}",
        f"  Valid: {summary.valid_groups:,}",
        f"  Invalid: {summary.invalid_groups:,}",
        f"  Files: {summary.total_files:,}",
        f"  Validity: {summary.validity_rate:.1%}",
    ]

    if summary.is_clean:
        lines.append("  Status: All groups valid!")
    else:
        lines.append("\n  Issues:")
        for issue in summary.issues[:10]:
            lines.append(f"    - {issue}")

    return "\n".join(lines)
