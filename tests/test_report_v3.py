"""Tests for DupeClean report v3 module."""

from __future__ import annotations

import json

import pytest

from dupeclean.report_v3 import (
    ReportDataV2,
    format_json_report_v2,
    format_markdown_report_v2,
    format_text_report_v2,
)


@pytest.fixture
def report_data():
    return ReportDataV2(
        operation_id="test_op",
        files_processed=100,
        files_deleted=50,
        files_hardlinked=30,
        space_freed=1024000,
        errors=2,
        duration=5.5,
        strategy="shortest",
        groups_processed=10,
    )


class TestFormatTextReportV2:
    def test_contains_stats(self, report_data):
        text = format_text_report_v2(report_data)
        assert "test_op" in text
        assert "100" in text
        assert "50" in text


class TestFormatJsonReportV2:
    def test_valid_json(self, report_data):
        text = format_json_report_v2(report_data)
        data = json.loads(text)
        assert data["operation_id"] == "test_op"
        assert data["files_processed"] == 100


class TestFormatMarkdownReportV2:
    def test_markdown_table(self, report_data):
        text = format_markdown_report_v2(report_data)
        assert "| Metric | Value |" in text
        assert "test_op" in text


class TestReportDataV2:
    def test_freed_display(self):
        data = ReportDataV2(operation_id="test", space_freed=1024)
        assert "B" in data.freed_display

    def test_success_rate(self):
        data = ReportDataV2(
            operation_id="test",
            files_processed=10,
            files_deleted=5,
            files_hardlinked=3,
        )
        assert data.success_rate == 0.8
