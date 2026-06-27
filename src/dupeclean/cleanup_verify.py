"""File deduplication cleanup verification for DupeClean.

Verify that cleanup operations completed successfully.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VerificationCheck:
    """A single verification check."""

    check_type: str
    path: str
    passed: bool
    message: str = ""

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"


@dataclass
class CleanupVerification:
    """Complete cleanup verification."""

    checks: list[VerificationCheck] = field(default_factory=list)

    def add(self, check: VerificationCheck) -> None:
        self.checks.append(check)

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    @property
    def is_clean(self) -> bool:
        return self.failed == 0

    def verify_file_deleted(self, path: Path) -> None:
        """Verify a file was deleted."""
        exists = path.exists()
        self.add(
            VerificationCheck(
                check_type="delete",
                path=str(path),
                passed=not exists,
                message="File still exists" if exists else "OK",
            )
        )

    def verify_file_exists(self, path: Path) -> None:
        """Verify a file exists (for kept files)."""
        exists = path.exists()
        self.add(
            VerificationCheck(
                check_type="exists",
                path=str(path),
                passed=exists,
                message="OK" if exists else "File missing",
            )
        )

    def verify_hardlink(self, source: Path, target: Path) -> None:
        """Verify two files are hardlinked."""
        try:
            s1 = source.stat()
            s2 = target.stat()
            same = s1.st_ino == s2.st_ino
            self.add(
                VerificationCheck(
                    check_type="hardlink",
                    path=str(target),
                    passed=same,
                    message="OK" if same else "Not hardlinked",
                )
            )
        except OSError as e:
            self.add(
                VerificationCheck(
                    check_type="hardlink",
                    path=str(target),
                    passed=False,
                    message=str(e),
                )
            )

    def render(self) -> str:
        """Render verification as text."""
        lines = [
            f"Cleanup Verification: {self.total_checks} checks",
            f"  Passed: {self.passed:,}",
            f"  Failed: {self.failed:,}",
            f"  Status: {'ALL OK' if self.is_clean else 'ISSUES FOUND'}",
        ]

        if not self.is_clean:
            lines.append("\n  Failed checks:")
            for check in self.checks:
                if not check.passed:
                    lines.append(f"    [{check.check_type}] {check.path}: {check.message}")

        return "\n".join(lines)
