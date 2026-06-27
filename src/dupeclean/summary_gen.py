"""File deduplication cleanup summary generator for DupeClean.

Generate comprehensive cleanup summaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import format_size


@dataclass
class SummarySection:
    """A section of a cleanup summary."""

    title: str
    content: str


@dataclass
class CleanupSummaryGenerator:
    """Generate cleanup summaries."""

    sections: list[SummarySection] = field(default_factory=list)

    def add_section(self, title: str, content: str) -> None:
        self.sections.append(SummarySection(title=title, content=content))

    def render(self) -> str:
        """Render summary as text."""
        if not self.sections:
            return "No summary data."

        lines = ["Cleanup Summary", "=" * 16, ""]
        for section in self.sections:
            lines.append(section.title)
            lines.append("-" * len(section.title))
            lines.append(section.content)
            lines.append("")
        return "\n".join(lines)


def generate_cleanup_summary(
    files_before: int,
    files_after: int,
    size_before: int,
    size_after: int,
    groups_cleaned: int,
    errors: int,
    duration: float,
) -> CleanupSummaryGenerator:
    """Generate a comprehensive cleanup summary."""
    gen = CleanupSummaryGenerator()

    freed = size_before - size_after
    reduction = (freed / size_before * 100) if size_before > 0 else 0

    gen.add_section(
        "Overview",
        f"  Files before: {files_before:,}\n"
        f"  Files after: {files_after:,}\n"
        f"  Groups cleaned: {groups_cleaned:,}\n"
        f"  Errors: {errors}",
    )

    gen.add_section(
        "Space",
        f"  Before: {format_size(size_before)}\n"
        f"  After: {format_size(size_after)}\n"
        f"  Freed: {format_size(freed)} ({reduction:.1f}%)",
    )

    gen.add_section(
        "Performance",
        f"  Duration: {duration:.1f}s\n  Files/second: {files_before / duration:.0f}"
        if duration > 0
        else "  Duration: N/A",
    )

    return gen


def format_summary(gen: CleanupSummaryGenerator) -> str:
    """Format summary as text."""
    return gen.render()
