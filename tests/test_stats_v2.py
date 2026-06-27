"""Tests for DupeClean cleanup statistics v2 module."""

from __future__ import annotations

from dupeclean.stats_v2 import (
    CleanupStatsV2,
    format_stats_v2,
)


class TestCleanupStatsV2:
    def test_space_freed(self):
        stats = CleanupStatsV2(space_before=1000, space_after=500)
        assert stats.space_freed == 500

    def test_reduction_pct(self):
        stats = CleanupStatsV2(space_before=1000, space_after=700)
        assert stats.reduction_pct == 30.0

    def test_zero_before(self):
        stats = CleanupStatsV2()
        assert stats.reduction_pct == 0.0

    def test_total_duration(self):
        stats = CleanupStatsV2(scan_duration=1.0, hash_duration=2.0, cleanup_duration=3.0)
        assert stats.total_duration == 6.0

    def test_dedup_rate(self):
        stats = CleanupStatsV2(files_analyzed=100, duplicates_found=25)
        assert stats.dedup_rate == 0.25

    def test_freed_display(self):
        stats = CleanupStatsV2(space_before=1024, space_after=0)
        assert "B" in stats.freed_display


class TestFormatStatsV2:
    def test_basic(self):
        stats = CleanupStatsV2(
            files_scanned=100,
            files_analyzed=100,
            space_before=10000,
            space_after=8000,
        )
        text = format_stats_v2(stats)
        assert "100" in text
        assert "20.0%" in text
