"""Tests for DupeClean group export module."""

from __future__ import annotations

import json
from pathlib import Path

from dupeclean.group_export import (
    export_groups_csv,
    export_groups_json,
    export_groups_text,
    format_export_summary,
    save_groups,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


def _make_groups() -> list[DuplicateGroup]:
    return [
        DuplicateGroup(
            group_id=0, hash_value="abc", file_size=1000,
            files=[_fi("/a"), _fi("/b"), _fi("/c")],
        ),
        DuplicateGroup(
            group_id=1, hash_value="def", file_size=2000,
            files=[_fi("/d"), _fi("/e")],
        ),
    ]


class TestExportGroupsJson:
    def test_valid_json(self):
        groups = _make_groups()
        text = export_groups_json(groups)
        data = json.loads(text)
        assert len(data) == 2
        assert data[0]["group_id"] == 0

    def test_empty(self):
        text = export_groups_json([])
        data = json.loads(text)
        assert len(data) == 0


class TestExportGroupsCsv:
    def test_csv_format(self):
        groups = _make_groups()
        text = export_groups_csv(groups)
        assert "group_id" in text
        assert "file_path" in text

    def test_rows(self):
        groups = _make_groups()
        text = export_groups_csv(groups)
        lines = text.strip().split("\n")
        assert len(lines) == 6  # header + 3 + 2


class TestExportGroupsText:
    def test_empty(self):
        assert "No duplicate" in export_groups_text([])

    def test_with_groups(self):
        groups = _make_groups()
        text = export_groups_text(groups)
        assert "Group #0" in text
        assert "Group #1" in text


class TestSaveGroups:
    def test_json(self, tmp_path):
        groups = _make_groups()
        path = tmp_path / "groups.json"
        save_groups(groups, path, "json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) == 2

    def test_csv(self, tmp_path):
        groups = _make_groups()
        path = tmp_path / "groups.csv"
        save_groups(groups, path, "csv")
        assert path.exists()


class TestFormatExportSummary:
    def test_basic(self):
        groups = _make_groups()
        text = format_export_summary(groups, Path("/out.json"), "json")
        assert "2 groups" in text
        assert "json" in text
