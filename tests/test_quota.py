"""Tests for DupeClean quota management module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DirInfo
from dupeclean.quota import (
    Quota,
    check_quota,
    create_quota,
    format_multi_quota,
    format_quota_status,
    update_quota_from_dirs,
)


class TestQuota:
    def test_usage_pct(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=500,
        )
        assert q.usage_pct == 50.0

    def test_remaining(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=300,
        )
        assert q.remaining == 700

    def test_is_exceeded(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=1500,
        )
        assert q.is_exceeded is True

    def test_is_not_exceeded(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=500,
        )
        assert q.is_exceeded is False

    def test_is_warning(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=850,
            warning_pct=80,
        )
        assert q.is_warning is True

    def test_is_not_warning(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=500,
            warning_pct=80,
        )
        assert q.is_warning is False


class TestCreateQuota:
    def test_basic(self):
        q = create_quota(Path("/test"), 10.0)
        assert q.limit_bytes == 10 * 1073741824

    def test_custom_warning(self):
        q = create_quota(Path("/test"), 10.0, warning_pct=90)
        assert q.warning_pct == 90


class TestCheckQuota:
    def test_ok(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=500,
        )
        status = check_quota(q)
        assert status.status == "ok"

    def test_warning(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=850,
        )
        status = check_quota(q)
        assert status.status == "warning"

    def test_exceeded(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=1500,
        )
        status = check_quota(q)
        assert status.status == "exceeded"


class TestUpdateQuotaFromDirs:
    def test_basic(self):
        q = Quota(path=Path("/test"), limit_bytes=1000)
        dirs = {
            Path("/test"): DirInfo(
                path=Path("/test"), total_size=500, file_count=10
            )
        }
        updated = update_quota_from_dirs(q, dirs)
        assert updated.current_usage == 500


class TestFormatQuotaStatus:
    def test_ok(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=500,
        )
        status = check_quota(q)
        text = format_quota_status(status)
        assert "50.0%" in text

    def test_exceeded(self):
        q = Quota(
            path=Path("/test"),
            limit_bytes=1000,
            current_usage=1500,
        )
        status = check_quota(q)
        text = format_quota_status(status)
        assert "150.0%" in text


class TestFormatMultiQuota:
    def test_empty(self):
        assert "No quotas" in format_multi_quota([])

    def test_with_statuses(self):
        q1 = Quota(
            path=Path("/a"),
            limit_bytes=1000,
            current_usage=500,
        )
        q2 = Quota(
            path=Path("/b"),
            limit_bytes=1000,
            current_usage=1500,
        )
        statuses = [check_quota(q1), check_quota(q2)]
        text = format_multi_quota(statuses)
        assert "50.0%" in text
        assert "150.0%" in text
