"""Disk space forecasting module for DupeClean.

Predicts when disk will be full based on:
- Current usage trends
- Growth rate from scan history
- File creation patterns
"""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from .models import format_size


@dataclass
class DiskInfo:
    """Current disk space information."""

    path: Path
    total: int
    used: int
    free: int

    @property
    def used_pct(self) -> float:
        return (self.used / self.total * 100) if self.total else 0

    @property
    def free_pct(self) -> float:
        return (self.free / self.total * 100) if self.total else 0

    @property
    def total_display(self) -> str:
        return format_size(self.total)

    @property
    def used_display(self) -> str:
        return format_size(self.used)

    @property
    def free_display(self) -> str:
        return format_size(self.free)


@dataclass
class Forecast:
    """Disk space forecast."""

    disk: DiskInfo
    daily_growth: float  # bytes per day
    days_until_full: float | None
    projected_full_date: str | None
    recommendation: str


def get_disk_info(path: Path) -> DiskInfo:
    """Get disk space information for the volume containing path."""
    usage = shutil.disk_usage(str(path))
    return DiskInfo(
        path=path,
        total=usage.total,
        used=usage.used,
        free=usage.free,
    )


def calculate_growth_rate(
    scan_history: list[dict],
) -> float:
    """Calculate daily growth rate from scan history.

    Args:
        scan_history: List of scan records with 'time' and 'size' keys.

    Returns:
        Estimated bytes per day growth rate.
    """
    if len(scan_history) < 2:
        return 0.0

    # Sort by time
    sorted_history = sorted(scan_history, key=lambda r: r["time"])

    # Calculate growth between first and last scan
    first = sorted_history[0]
    last = sorted_history[-1]

    time_diff = last["time"] - first["time"]
    if time_diff <= 0:
        return 0.0

    size_diff = last["size"] - first["size"]
    daily_rate = size_diff / (time_diff / 86400)  # seconds to days

    return daily_rate


def forecast_disk_space(
    path: Path,
    daily_growth: float = 0.0,
) -> Forecast:
    """Forecast when disk will be full.

    Args:
        path: Path on the disk to forecast.
        daily_growth: Estimated daily growth in bytes.

    Returns:
        Forecast with predictions.
    """
    disk = get_disk_info(path)

    days_until_full: float | None = None
    projected_date: str | None = None

    if daily_growth > 0 and disk.free > 0:
        days_until_full = disk.free / daily_growth
        import datetime

        full_time = time.time() + (days_until_full * 86400)
        projected_date = datetime.datetime.fromtimestamp(full_time).strftime("%Y-%m-%d")

    # Generate recommendation
    if disk.used_pct > 90:
        recommendation = "CRITICAL: Disk is over 90% full! Consider cleaning up immediately."
    elif disk.used_pct > 80:
        recommendation = "WARNING: Disk is over 80% full. Plan cleanup soon."
    elif days_until_full and days_until_full < 30:
        recommendation = (
            f"Disk may fill up in {days_until_full:.0f} days. "
            f"Consider running dupeclean --duplicates"
        )
    elif days_until_full and days_until_full < 90:
        recommendation = f"Disk projected full in {days_until_full:.0f} days. Monitor usage."
    else:
        recommendation = "Disk space looks healthy."

    return Forecast(
        disk=disk,
        daily_growth=daily_growth,
        days_until_full=days_until_full,
        projected_full_date=projected_date,
        recommendation=recommendation,
    )


def format_forecast(forecast: Forecast) -> str:
    """Format a forecast as human-readable text."""
    d = forecast.disk
    lines = [
        f"Disk: {d.path}",
        f"  Total: {d.total_display}",
        f"  Used:  {d.used_display} ({d.used_pct:.1f}%)",
        f"  Free:  {d.free_display} ({d.free_pct:.1f}%)",
        "",
    ]

    if forecast.daily_growth > 0:
        lines.append(f"  Daily growth: {format_size(int(forecast.daily_growth))}")
        if forecast.days_until_full is not None:
            lines.append(f"  Days until full: {forecast.days_until_full:.0f}")
            if forecast.projected_full_date:
                lines.append(f"  Projected full: {forecast.projected_full_date}")

    lines.extend(["", f"  {forecast.recommendation}"])

    # Usage bar
    bar_width = 40
    filled = int(forecast.disk.used_pct / 100 * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.insert(3, f"  [{bar}] {forecast.disk.used_pct:.1f}%")

    return "\n".join(lines)
