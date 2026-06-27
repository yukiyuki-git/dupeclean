"""Tests for DupeClean savings calculator module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.savings import (
    SavingsBreakdown,
    calculate_actual_savings,
    calculate_savings,
    format_savings,
)


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(size: int, count: int, ext: str = ".txt") -> DuplicateGroup:
    return DuplicateGroup(
        group_id=0,
        hash_value="abc",
        file_size=size,
        files=[_fi(f"/f{i}{ext}", size) for i in range(count)],
    )


class TestCalculateSavings:
    def test_basic(self):
        groups = [
            _group(1000, 3),
            _group(2000, 2),
        ]
        breakdown = calculate_savings(groups)
        assert breakdown.total_savings == 4000  # 2000 + 2000

    def test_by_size(self):
        groups = [_group(100, 3), _group(50000, 2)]
        breakdown = calculate_savings(groups)
        assert "<1KB" in breakdown.by_size
        assert "1-64KB" in breakdown.by_size

    def test_by_extension(self):
        groups = [
            _group(100, 3, ".txt"),
            _group(200, 2, ".py"),
        ]
        breakdown = calculate_savings(groups)
        assert ".txt" in breakdown.by_extension
        assert ".py" in breakdown.by_extension

    def test_empty(self):
        breakdown = calculate_savings([])
        assert breakdown.total_savings == 0


class TestSavingsBreakdown:
    def test_savings_display(self):
        breakdown = SavingsBreakdown(total_savings=1024)
        assert "B" in breakdown.savings_display


class TestCalculateActualSavings:
    def test_basic(self):
        result = calculate_actual_savings(100, 10000, 95, 8000)
        assert result["files_removed"] == 5
        assert result["space_freed"] == 2000
        assert result["reduction_pct"] == 20.0

    def test_zero_before(self):
        result = calculate_actual_savings(0, 0, 0, 0)
        assert result["reduction_pct"] == 0


class TestFormatSavings:
    def test_basic(self):
        breakdown = SavingsBreakdown(
            total_savings=1000,
            by_size={"<1KB": 500, "1-64KB": 500},
        )
        text = format_savings(breakdown)
        assert "1,000" in text or "B" in text
        assert "<1KB" in text
