"""Tests for DupeClean cleanup analyzer module."""

from __future__ import annotations

from dupeclean.cleanup_analyzer import (
    CleanupAnalysis,
    analyze_cleanup,
    format_cleanup_analysis,
)


class TestAnalyzeCleanup:
    def test_basic(self):
        analysis = analyze_cleanup(
            total_groups=10,
            groups_cleaned=8,
            total_files=100,
            files_removed=20,
            space_before=10000,
            space_freed=2000,
        )
        assert analysis.cleanup_rate == 0.8
        assert analysis.file_reduction == 0.2
        assert analysis.space_reduction == 20.0


class TestCleanupAnalysis:
    def test_zero_totals(self):
        analysis = CleanupAnalysis()
        assert analysis.cleanup_rate == 0.0
        assert analysis.file_reduction == 0.0
        assert analysis.space_reduction == 0.0

    def test_freed_display(self):
        analysis = CleanupAnalysis(space_freed=1024)
        assert "B" in analysis.freed_display


class TestFormatCleanupAnalysis:
    def test_basic(self):
        analysis = analyze_cleanup(10, 8, 100, 20, 10000, 2000)
        text = format_cleanup_analysis(analysis)
        assert "80.0%" in text
        assert "20.0%" in text
