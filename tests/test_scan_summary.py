"""Tests for DupeClean scan summary module."""

from __future__ import annotations

from dupeclean.models import ScanStats
from dupeclean.scan_summary import (
    ScanSummary,
    create_scan_summary,
    format_brief_summary,
    format_scan_summary,
)


class TestScanSummary:
    def test_size_display(self):
        summary = ScanSummary(total_size=1024)
        assert "B" in summary.size_display

    def test_dupe_pct(self):
        summary = ScanSummary(total_files=100, duplicate_files=25)
        assert summary.dupe_pct == 25.0

    def test_waste_pct(self):
        summary = ScanSummary(total_size=1000, wasted_space=200)
        assert summary.waste_pct == 20.0

    def test_zero_totals(self):
        summary = ScanSummary()
        assert summary.dupe_pct == 0.0
        assert summary.waste_pct == 0.0


class TestCreateScanSummary:
    def test_basic(self):
        stats = ScanStats(
            total_files=100,
            total_dirs=10,
            total_size=10000,
            scan_duration=1.5,
            duplicate_groups=5,
            duplicate_files=15,
            wasted_space=3000,
        )
        summary = create_scan_summary(stats)
        assert summary.total_files == 100
        assert summary.duplicate_groups == 5


class TestFormatScanSummary:
    def test_basic(self):
        summary = ScanSummary(
            total_files=100,
            total_dirs=10,
            total_size=10000,
        )
        text = format_scan_summary(summary)
        assert "100" in text
        assert "Scan Summary" in text

    def test_with_duplicates(self):
        summary = ScanSummary(
            total_files=100,
            duplicate_groups=5,
            duplicate_files=15,
            wasted_space=3000,
        )
        text = format_scan_summary(summary)
        assert "Duplicate" in text


class TestFormatBriefSummary:
    def test_basic(self):
        summary = ScanSummary(total_files=100, total_size=10000)
        text = format_brief_summary(summary)
        assert "100" in text

    def test_with_duplicates(self):
        summary = ScanSummary(
            total_files=100,
            duplicate_groups=5,
            wasted_space=3000,
        )
        text = format_brief_summary(summary)
        assert "dupe" in text
