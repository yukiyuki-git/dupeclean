"""File deduplication cleanup feedback module for DupeClean.

Provide feedback on cleanup operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class FeedbackItem:
    """A feedback item."""

    category: str  # "success", "warning", "info", "error"
    message: str
    details: str = ""


@dataclass
class CleanupFeedback:
    """Feedback on a cleanup operation."""

    items: list[FeedbackItem] = field(default_factory=list)

    def success(self, message: str, details: str = "") -> None:
        self.items.append(FeedbackItem(category="success", message=message, details=details))

    def warning(self, message: str, details: str = "") -> None:
        self.items.append(FeedbackItem(category="warning", message=message, details=details))

    def info(self, message: str, details: str = "") -> None:
        self.items.append(FeedbackItem(category="info", message=message, details=details))

    def error(self, message: str, details: str = "") -> None:
        self.items.append(FeedbackItem(category="error", message=message, details=details))

    @property
    def has_errors(self) -> bool:
        return any(i.category == "error" for i in self.items)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.items if i.category == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.items if i.category == "warning")

    def render(self) -> str:
        """Render feedback as text."""
        icons = {
            "success": "[+]",
            "warning": "[!]",
            "info": "[i]",
            "error": "[X]",
        }
        lines = [
            f"Feedback: {len(self.items)} items "
            f"({self.error_count} errors, {self.warning_count} warnings)",
            "",
        ]
        for item in self.items:
            icon = icons.get(item.category, "[?]")
            lines.append(f"  {icon} {item.message}")
            if item.details:
                lines.append(f"     {item.details}")
        return "\n".join(lines)


def generate_feedback(
    files_processed: int,
    files_deleted: int,
    space_freed: int,
    errors: list[str],
) -> CleanupFeedback:
    """Generate feedback from cleanup results."""
    feedback = CleanupFeedback()

    if files_deleted > 0:
        feedback.success(
            f"Deleted {files_deleted:,} files",
            f"Freed {format_size(space_freed)}",
        )

    if errors:
        for error in errors[:5]:
            feedback.error(error)
        if len(errors) > 5:
            feedback.warning(f"... and {len(errors) - 5} more errors")

    if files_processed == 0:
        feedback.info("No files to process")

    return feedback
