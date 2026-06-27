"""Tests for DupeClean cleanup report module."""

from __future__ import annotations

from dupeclean.cleanup_report import (
    CleanupReport,
    CleanupReportEntry,
    generate_cleanup_report,
)


class TestCleanupReport:
    def test_add(self):
        report = CleanupReport(operation_id="test")
        report.add(CleanupReportEntry(file_path="/a", action="delete"))
        assert report.total_entries == 1

    def test_success_count(self):
        report = CleanupReport(operation_id="test")
        report.add(CleanupReportEntry(file_path="/a", action="delete", success=True))
        report.add(CleanupReportEntry(file_path="/b", action="delete", success=False))
        assert report.success_count == 1

    def test_error_count(self):
        report = CleanupReport(operation_id="test")
        report.add(CleanupReportEntry(file_path="/a", action="delete", success=True))
        report.add(CleanupReportEntry(file_path="/b", action="delete", success=False))
        assert report.error_count == 1

    def test_total_freed(self):
        report = CleanupReport(operation_id="test")
        report.add(CleanupReportEntry(file_path="/a", action="delete", size=100, success=True))
        report.add(CleanupReportEntry(file_path="/b", action="delete", size=200, success=True))
        assert report.total_freed == 300

    def test_render(self):
        report = CleanupReport(operation_id="test")
        report.add(CleanupReportEntry(file_path="/a.txt", action="delete", size=100))
        text = report.render()
        assert "test" in text
        assert "delete" in text


class TestGenerateCleanupReport:
    def test_basic(self):
        files = [
            ("/a.txt", "delete", 100, True, ""),
            ("/b.txt", "delete", 200, False, "error"),
        ]
        report = generate_cleanup_report("test_op", files)
        assert report.total_entries == 2
        assert report.success_count == 1


class TestCleanupReportEntry:
    def test_size_display(self):
        entry = CleanupReportEntry(file_path="/a", action="delete", size=1024)
        assert "B" in entry.size_display
