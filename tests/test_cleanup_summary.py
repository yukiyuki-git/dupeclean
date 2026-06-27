"""Tests for DupeClean cleanup summary module."""

from __future__ import annotations

from dupeclean.cleanup_summary import (
    CleanupSummary,
    create_summary,
    format_brief_summary,
    format_cleanup_summary,
)


class TestCleanupSummary:
    def test_space_freed(self):
        summary = CleanupSummary(
            operation_id="test",
            size_before=1000,
            size_after=500,
        )
        assert summary.space_freed == 500

    def test_reduction_pct(self):
        summary = CleanupSummary(
            operation_id="test",
            size_before=1000,
            size_after=700,
        )
        assert summary.reduction_pct == 30.0

    def test_files_removed(self):
        summary = CleanupSummary(
            operation_id="test",
            files_before=10,
            files_after=7,
        )
        assert summary.files_removed == 3


class TestCreateSummary:
    def test_basic(self):
        summary = create_summary("test", 100, 10000, files_deleted=5)
        assert summary.files_before == 100
        assert summary.files_deleted == 5

    def test_with_errors(self):
        summary = create_summary("test", 100, 10000, errors=2)
        assert summary.errors == 2


class TestFormatCleanupSummary:
    def test_basic(self):
        summary = CleanupSummary(
            operation_id="test",
            files_before=100,
            files_after=95,
            size_before=10000,
            size_after=8000,
        )
        text = format_cleanup_summary(summary)
        assert "test" in text
        assert "100" in text
        assert "95" in text

    def test_with_freed(self):
        summary = CleanupSummary(
            operation_id="test",
            size_before=1000,
            size_after=500,
        )
        text = format_cleanup_summary(summary)
        assert "Freed" in text


class TestFormatBriefSummary:
    def test_basic(self):
        summary = CleanupSummary(
            operation_id="test",
            files_before=100,
            files_after=95,
            files_deleted=5,
            size_before=10000,
            size_after=8000,
        )
        text = format_brief_summary(summary)
        assert "5" in text
        assert "freed" in text
