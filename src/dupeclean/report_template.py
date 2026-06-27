"""File deduplication cleanup report template module for DupeClean.

Templates for generating cleanup reports.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReportTemplate:
    """A report template."""

    name: str
    format: str  # "text", "json", "html", "markdown"
    template: str
    description: str = ""


# Built-in templates
TEMPLATES = {
    "summary": ReportTemplate(
        name="Summary",
        format="text",
        template="Cleanup: {files_deleted} deleted, {space_freed} freed",
        description="Brief one-line summary",
    ),
    "detailed": ReportTemplate(
        name="Detailed",
        format="text",
        template=(
            "Cleanup Report: {operation_id}\n"
            "  Processed: {files_processed}\n"
            "  Deleted: {files_deleted}\n"
            "  Freed: {space_freed}\n"
            "  Duration: {duration}s"
        ),
        description="Detailed text report",
    ),
    "json": ReportTemplate(
        name="JSON",
        format="json",
        template='{"deleted": {files_deleted}, "freed": {space_freed}}',
        description="JSON format",
    ),
}


def get_template(name: str) -> ReportTemplate:
    """Get a template by name."""
    return TEMPLATES.get(name, TEMPLATES["summary"])


def list_templates() -> list[ReportTemplate]:
    """List all templates."""
    return list(TEMPLATES.values())


def render_template(
    template: ReportTemplate,
    **kwargs,
) -> str:
    """Render a template with data."""
    result = template.template
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result
