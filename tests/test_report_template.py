"""Tests for DupeClean report template module."""

from __future__ import annotations

from dupeclean.report_template import (
    TEMPLATES,
    ReportTemplate,
    get_template,
    list_templates,
    render_template,
)


class TestGetTemplate:
    def test_summary(self):
        template = get_template("summary")
        assert template.name == "Summary"

    def test_unknown(self):
        template = get_template("unknown")
        assert template.name == "Summary"


class TestListTemplates:
    def test_has_templates(self):
        templates = list_templates()
        assert len(templates) >= 3


class TestRenderTemplate:
    def test_basic(self):
        template = get_template("summary")
        result = render_template(template, files_deleted=10, space_freed="1.0 KiB")
        assert "10" in result
        assert "1.0 KiB" in result

    def test_detailed(self):
        template = get_template("detailed")
        result = render_template(
            template,
            operation_id="test",
            files_processed=100,
            files_deleted=50,
            space_freed="1.0 KiB",
            duration="5.0",
        )
        assert "test" in result
        assert "50" in result


class TestReportTemplate:
    def test_defaults(self):
        template = ReportTemplate(name="test", format="text", template="test")
        assert template.description == ""


class TestTemplates:
    def test_all_exist(self):
        expected = {"summary", "detailed", "json"}
        assert set(TEMPLATES.keys()) == expected
