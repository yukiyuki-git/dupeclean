"""File quota management module for DupeClean.

Monitor and enforce disk usage quotas per directory.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import DirInfo, format_size


@dataclass
class Quota:
    """A disk usage quota."""

    path: Path
    limit_bytes: int
    warning_pct: float = 80.0  # Warn at this percentage
    current_usage: int = 0

    @property
    def usage_pct(self) -> float:
        if self.limit_bytes == 0:
            return 0.0
        return (self.current_usage / self.limit_bytes) * 100

    @property
    def remaining(self) -> int:
        return max(0, self.limit_bytes - self.current_usage)

    @property
    def is_exceeded(self) -> bool:
        return self.current_usage > self.limit_bytes

    @property
    def is_warning(self) -> bool:
        return self.usage_pct >= self.warning_pct

    @property
    def limit_display(self) -> str:
        return format_size(self.limit_bytes)

    @property
    def usage_display(self) -> str:
        return format_size(self.current_usage)

    @property
    def remaining_display(self) -> str:
        return format_size(self.remaining)


@dataclass
class QuotaStatus:
    """Status of a quota check."""

    quota: Quota
    status: str  # "ok", "warning", "exceeded"
    message: str


def create_quota(
    path: Path,
    limit_gb: float,
    warning_pct: float = 80.0,
) -> Quota:
    """Create a quota with a GB limit."""
    return Quota(
        path=path,
        limit_bytes=int(limit_gb * 1073741824),
        warning_pct=warning_pct,
    )


def check_quota(quota: Quota) -> QuotaStatus:
    """Check quota status."""
    if quota.is_exceeded:
        return QuotaStatus(
            quota=quota,
            status="exceeded",
            message=(
                f"EXCEEDED: {quota.usage_display} / {quota.limit_display} ({quota.usage_pct:.1f}%)"
            ),
        )
    if quota.is_warning:
        return QuotaStatus(
            quota=quota,
            status="warning",
            message=(
                f"WARNING: {quota.usage_display} / {quota.limit_display} ({quota.usage_pct:.1f}%)"
            ),
        )
    return QuotaStatus(
        quota=quota,
        status="ok",
        message=(f"OK: {quota.usage_display} / {quota.limit_display} ({quota.usage_pct:.1f}%)"),
    )


def update_quota_from_dirs(quota: Quota, dirs: dict[Path, DirInfo]) -> Quota:
    """Update quota with current usage from scan results."""
    dir_info = dirs.get(quota.path)
    if dir_info:
        quota.current_usage = dir_info.total_size
    return quota


def format_quota_status(status: QuotaStatus) -> str:
    """Format quota status as text."""
    q = status.quota
    icons = {"ok": "[+]", "warning": "[!]", "exceeded": "[X]"}
    icon = icons.get(status.status, "[?]")

    bar_width = 30
    filled = min(bar_width, int(q.usage_pct / 100 * bar_width))
    bar = "█" * filled + "░" * (bar_width - filled)

    lines = [
        f"{icon} Quota: {q.path}",
        f"  [{bar}] {q.usage_pct:.1f}%",
        f"  Used: {q.usage_display}",
        f"  Limit: {q.limit_display}",
        f"  Remaining: {q.remaining_display}",
        f"  Status: {status.message}",
    ]
    return "\n".join(lines)


def format_multi_quota(
    statuses: list[QuotaStatus],
) -> str:
    """Format multiple quota statuses."""
    if not statuses:
        return "No quotas configured."

    lines = ["Quota Status:", ""]
    for status in statuses:
        q = status.quota
        level = "exceeded" if q.is_exceeded else "warning" if q.is_warning else "ok"
        icon = {"ok": "[+]", "warning": "[!]", "exceeded": "[X]"}.get(level, "[?]")
        lines.append(f"  {icon} {q.path}: {q.usage_display}/{q.limit_display} ({q.usage_pct:.1f}%)")

    return "\n".join(lines)
