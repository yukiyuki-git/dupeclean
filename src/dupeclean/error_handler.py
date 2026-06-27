"""File deduplication error handling module for DupeClean.

Centralized error handling for dedup operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DedupError:
    """A dedup operation error."""

    error_type: str
    message: str
    path: str = ""
    recoverable: bool = True
    context: dict = field(default_factory=dict)


@dataclass
class ErrorHandler:
    """Centralized error handler for dedup operations."""

    errors: list[DedupError] = field(default_factory=list)
    max_errors: int = 1000

    def add(
        self,
        error_type: str,
        message: str,
        path: str = "",
        recoverable: bool = True,
        **context,
    ) -> None:
        """Add an error."""
        if len(self.errors) >= self.max_errors:
            return
        self.errors.append(
            DedupError(
                error_type=error_type,
                message=message,
                path=path,
                recoverable=recoverable,
                context=context,
            )
        )

    def add_os_error(self, error: OSError, path: str = "") -> None:
        """Add an OS error."""
        self.add(
            "os_error",
            str(error),
            path=path,
            recoverable=True,
        )

    def add_permission_error(self, path: str) -> None:
        """Add a permission error."""
        self.add(
            "permission",
            f"Permission denied: {path}",
            path=path,
            recoverable=False,
        )

    @property
    def count(self) -> int:
        return len(self.errors)

    @property
    def recoverable_count(self) -> int:
        return sum(1 for e in self.errors if e.recoverable)

    @property
    def critical_count(self) -> int:
        return sum(1 for e in self.errors if not e.recoverable)

    @property
    def has_critical(self) -> bool:
        return self.critical_count > 0

    def get_by_type(self, error_type: str) -> list[DedupError]:
        """Get errors by type."""
        return [e for e in self.errors if e.error_type == error_type]

    def clear(self) -> None:
        """Clear all errors."""
        self.errors.clear()


def format_errors(handler: ErrorHandler) -> str:
    """Format errors as text."""
    if not handler.errors:
        return "No errors."

    lines = [
        f"Errors: {handler.count} "
        f"({handler.critical_count} critical, "
        f"{handler.recoverable_count} recoverable)",
        "",
    ]

    # Group by type
    by_type: dict[str, list[DedupError]] = {}
    for error in handler.errors:
        by_type.setdefault(error.error_type, []).append(error)

    for error_type, errors in by_type.items():
        lines.append(f"  [{error_type}] ({len(errors)} errors)")
        for e in errors[:3]:
            lines.append(f"    {e.message}")
        if len(errors) > 3:
            lines.append(f"    ... and {len(errors) - 3} more")

    return "\n".join(lines)
