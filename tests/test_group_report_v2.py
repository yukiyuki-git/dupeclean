"""Tests for DupeClean group reporter v2 module."""

from __future__ import annotations

import json
from pathlib import Path

from dupeclean.group_report_v2 import (
    GroupReportData,
    format_group_report_data,
    generate_group_report_json,
    generate_group_report_text,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _group(gid: int, size: int, count: int) -> DuplicateGroup:
    return DuplicateGroup(
        group_id=gid,
        hash_value=f"h{gid}",
        file_size=size,
        files=[_fi(f"/f{i}", size) for i in range(count)],
    )


class TestGenerateGroupReportText:
    def test_basic(self):
        data = GroupReportData(
            groups=[_group(0, 100, 3)],
            total_files=10,
            total_size=5000,
            scan_duration=1.5,
        )
        text = generate_group_report_text(data)
        assert "Groups:" in text
        assert "10" in text

    def test_with_cleanup(self):
        data = GroupReportData(
            groups=[_group(0, 100, 3)],
            files_cleaned=5,
            space_freed=1000,
            cleanup_duration=2.0,
        )
        text = generate_group_report_text(data)
        assert "cleaned" in text.lower() or "freed" in text.lower()


class TestGenerateGroupReportJson:
    def test_valid_json(self):
        data = GroupReportData(
            groups=[_group(0, 100, 3)],
            total_files=10,
            total_size=5000,
        )
        text = generate_group_report_json(data)
        result = json.loads(text)
        assert result["groups"] == 1
        assert result["total_files"] == 10


class TestFormatGroupReportData:
    def test_basic(self):
        data = GroupReportData(groups=[_group(0, 100, 2)])
        text = format_group_report_data(data)
        assert "DupeClean" in text


class TestGroupReportData:
    def test_wasted_display(self):
        data = GroupReportData(groups=[_group(0, 100, 3)])
        assert "B" in data.wasted_display
