"""Tests for DupeClean disk space forecasting."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from dupeclean.forecast import (
    DiskInfo,
    Forecast,
    calculate_growth_rate,
    forecast_disk_space,
    format_forecast,
    get_disk_info,
)


class TestGetDiskInfo:
    def test_returns_valid_info(self, tmp_path):
        info = get_disk_info(tmp_path)
        assert info.total > 0
        assert info.used >= 0
        assert info.free >= 0
        assert info.total == info.used + info.free

    def test_percentages(self, tmp_path):
        info = get_disk_info(tmp_path)
        assert 0 <= info.used_pct <= 100
        assert 0 <= info.free_pct <= 100
        assert abs(info.used_pct + info.free_pct - 100) < 0.1

    def test_display_properties(self, tmp_path):
        info = get_disk_info(tmp_path)
        assert "B" in info.total_display
        assert "B" in info.used_display
        assert "B" in info.free_display


class TestDiskInfo:
    def test_custom_disk_info(self):
        info = DiskInfo(
            path=Path("/test"),
            total=1000,
            used=750,
            free=250,
        )
        assert info.used_pct == 75.0
        assert info.free_pct == 25.0


class TestCalculateGrowthRate:
    def test_positive_growth(self):
        now = time.time()
        history = [
            {"time": now - 86400 * 10, "size": 1000},
            {"time": now, "size": 2000},
        ]
        rate = calculate_growth_rate(history)
        assert rate == pytest.approx(100.0, rel=0.1)

    def test_negative_growth(self):
        now = time.time()
        history = [
            {"time": now - 86400 * 5, "size": 2000},
            {"time": now, "size": 1000},
        ]
        rate = calculate_growth_rate(history)
        assert rate < 0

    def test_single_entry(self):
        history = [{"time": 100, "size": 1000}]
        assert calculate_growth_rate(history) == 0.0

    def test_empty_history(self):
        assert calculate_growth_rate([]) == 0.0

    def test_same_time(self):
        history = [
            {"time": 100, "size": 1000},
            {"time": 100, "size": 2000},
        ]
        assert calculate_growth_rate(history) == 0.0


class TestForecastDiskSpace:
    def test_basic_forecast(self, tmp_path):
        forecast = forecast_disk_space(tmp_path)
        assert isinstance(forecast, Forecast)
        assert forecast.disk.total > 0

    def test_with_growth_rate(self, tmp_path):
        forecast = forecast_disk_space(
            tmp_path,
            daily_growth=1024 * 1024,  # 1MB/day
        )
        assert forecast.daily_growth == 1024 * 1024
        assert forecast.days_until_full is not None

    def test_zero_growth(self, tmp_path):
        forecast = forecast_disk_space(tmp_path, daily_growth=0)
        assert forecast.days_until_full is None


class TestFormatForecast:
    def test_contains_disk_info(self, tmp_path):
        forecast = forecast_disk_space(tmp_path)
        text = format_forecast(forecast)
        assert "Disk:" in text
        assert "Total:" in text
        assert "Used:" in text
        assert "Free:" in text

    def test_contains_bar(self, tmp_path):
        forecast = forecast_disk_space(tmp_path)
        text = format_forecast(forecast)
        assert "█" in text or "░" in text

    def test_with_growth(self, tmp_path):
        forecast = forecast_disk_space(tmp_path, daily_growth=1024 * 1024)
        text = format_forecast(forecast)
        assert "Daily growth" in text
