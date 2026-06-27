"""File deduplication cleanup validator for DupeClean.

Validate cleanup plans before execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import DuplicateGroup


@dataclass
class ValidationIssue:
    """A validation issue."""

    severity: str  # "warning", "error"
    message: str
    path: str = ""

    @property
    def icon(self) -> str:
        return "[!]" if self.severity == "warning" else "[X]"


@dataclass
class PlanValidation:
    """Validation result for a cleanup plan."""

    is_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    groups_checked: int = 0
    files_checked: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def add_issue(self, severity: str, message: str, path: str = "") -> None:
        self.issues.append(ValidationIssue(severity=severity, message=message, path=path))
        if severity == "error":
            self.is_valid = False


def validate_groups(groups: list[DuplicateGroup]) -> PlanValidation:
    """Validate duplicate groups before cleanup.

    Checks:
    - All files exist
    - All files have consistent sizes
    - No single-file groups
    - No zero-size files
    """
    validation = PlanValidation(groups_checked=len(groups))

    for group in groups:
        if len(group.files) < 2:
            validation.add_issue(
                "warning",
                f"Group #{group.group_id} has only {len(group.files)} file(s)",
            )
            continue

        # Check sizes
        sizes = set(f.size for f in group.files)
        if len(sizes) > 1:
            validation.add_issue(
                "error",
                f"Group #{group.group_id} has inconsistent sizes: {sizes}",
            )

        # Check zero-size
        if group.file_size == 0:
            validation.add_issue(
                "warning",
                f"Group #{group.group_id} has zero-size files",
            )

        # Check files exist
        for fi in group.files:
            validation.files_checked += 1
            if not fi.path.exists():
                validation.add_issue(
                    "error",
                    f"File not found: {fi.path}",
                    str(fi.path),
                )

    return validation


def format_validation(validation: PlanValidation) -> str:
    """Format validation result as text."""
    lines = [
        "Plan Validation:",
        f"  Groups: {validation.groups_checked}",
        f"  Files: {validation.files_checked}",
        f"  Errors: {validation.error_count}",
        f"  Warnings: {validation.warning_count}",
        f"  Status: {'VALID' if validation.is_valid else 'INVALID'}",
    ]

    if validation.issues:
        lines.append("\n  Issues:")
        for issue in validation.issues[:15]:
            lines.append(f"    {issue.icon} [{issue.severity}] {issue.message}")

    return "\n".join(lines)
