"""Tests for DupeClean report formatter module."""

from __future__ import annotations

import json

import pytest

from dupeclean.report_formatter import (
    ReportData,
    format_csv_report,
    format_html_report,
    format_json_report,
    format_markdown_report,
    format_text_report,
)


@pytest.fixture
def report_data():
    return ReportData(
        operation_id="test_op",
        files_processed=100,
        files_deleted=50,
        files_hardlinked=30,
        space_freed=1024000,
        errors=2,
        duration=5.5,
        strategy="shortest",
    )


class TestFormatTextReport:
    def test_contains_stats(self, report_data):
        text = format_text_report(report_data)
        assert "test_op" in text
        assert "100" in text
        assert "50" in text


class TestFormatJsonReport:
    def test_valid_json(self, report_data):
        text = format_json_report(report_data)
        data = json.loads(text)
        assert data["operation_id"] == "test_op"
        assert data["files_processed"] == 100


class TestFormatCsvReport:
    def test_csv_format(self, report_data):
        text = format_csv_report(report_data)
        assert "operation_id" in text
        assert "test_op" in text


class TestFormatHtmlReport:
    def test_html_structure(self, report_data):
        text = format_html_report(report_data)
        assert "<!DOCTYPE html>" in text
        assert "test_op" in text


class TestFormatMarkdownReport:
    def test_markdown_table(self, report_data):
        text = format_markdown_report(report_data)
        assert "| Metric | Value |" in text
        assert "test_op" in text


class TestReportData:
    def test_freed_display(self):
        data = ReportData(operation_id="test", space_freed=1024)
        assert "B" in data.freed_display
