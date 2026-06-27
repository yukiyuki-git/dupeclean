"""Tests for DupeClean cleanup reporter v2 module."""

from __future__ import annotations

from dupeclean.cleanup_report_v2 import (
    CleanupReportV2,
    CleanupStats,
    create_report,
    format_cleanup_report_v2,
)


class TestCleanupStats:
    def test_space_freed(self):
        stats = CleanupStats(size_before=1000, size_after=500)
        assert stats.space_freed == 500

    def test_reduction_pct(self):
        stats = CleanupStats(size_before=1000, size_after=700)
        assert stats.reduction_pct == 30.0

    def test_zero_before(self):
        stats = CleanupStats(size_before=0, size_after=0)
        assert stats.reduction_pct == 0.0

    def test_freed_display(self):
        stats = CleanupStats(size_before=1024, size_after=0)
        assert "B" in stats.freed_display


class TestCleanupReportV2:
    def test_render(self):
        stats = CleanupStats(
            files_before=100,
            files_after=95,
            size_before=10000,
            size_after=8000,
            files_deleted=5,
        )
        report = CleanupReportV2(
            stats=stats,
            operation_id="test_op",
            timestamp=1000000,
            strategy="shortest",
        )
        text = report.render()
        assert "test_op" in text
        assert "shortest" in text
        assert "95" in text

    def test_with_details(self):
        stats = CleanupStats(files_deleted=1)
        report = CleanupReportV2(
            stats=stats,
            operation_id="test",
            timestamp=1000000,
            strategy="newest",
            details=["Deleted file_a.txt", "Deleted file_b.txt"],
        )
        text = report.render()
        assert "file_a.txt" in text


class TestCreateReport:
    def test_basic(self):
        stats = CleanupStats(files_deleted=5, size_before=10000, size_after=8000)
        report = create_report(stats, strategy="shortest")
        assert report.operation_id.startswith("cleanup_")


class TestFormatCleanupReportV2:
    def test_basic(self):
        stats = CleanupStats()
        report = create_report(stats)
        text = format_cleanup_report_v2(report)
        assert "Cleanup Report" in text
