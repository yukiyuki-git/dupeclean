"""Tests for DupeClean cleanup result module."""

from __future__ import annotations

from dupeclean.result import (
    CleanupOutcome,
    CleanupResultV2,
    format_cleanup_result_v2,
)


class TestCleanupResultV2:
    def test_add(self):
        result = CleanupResultV2(operation_id="test")
        result.add(CleanupOutcome(path="/a", action="delete", success=True))
        assert result.total_outcomes == 1

    def test_success_count(self):
        result = CleanupResultV2(operation_id="test")
        result.add(CleanupOutcome(path="/a", action="delete", success=True))
        result.add(CleanupOutcome(path="/b", action="delete", success=False))
        assert result.success_count == 1

    def test_error_count(self):
        result = CleanupResultV2(operation_id="test")
        result.add(CleanupOutcome(path="/a", action="delete", success=True))
        result.add(CleanupOutcome(path="/b", action="delete", success=False))
        assert result.error_count == 1

    def test_total_freed(self):
        result = CleanupResultV2(operation_id="test")
        result.add(CleanupOutcome(path="/a", action="delete", success=True, size=100))
        result.add(CleanupOutcome(path="/b", action="delete", success=False, size=200))
        assert result.total_freed == 100


class TestCleanupOutcome:
    def test_size_display(self):
        outcome = CleanupOutcome(path="/a", action="delete", success=True, size=1024)
        assert "B" in outcome.size_display


class TestFormatCleanupResultV2:
    def test_basic(self):
        result = CleanupResultV2(operation_id="test")
        result.add(CleanupOutcome(path="/a", action="delete", success=True))
        text = format_cleanup_result_v2(result)
        assert "test" in text
        assert "1" in text

    def test_with_errors(self):
        result = CleanupResultV2(operation_id="test")
        result.add(
            CleanupOutcome(path="/a", action="delete", success=False, error="Permission denied")
        )
        text = format_cleanup_result_v2(result)
        assert "Permission denied" in text
