"""Tests for DupeClean group import module."""

from __future__ import annotations

import json

from dupeclean.group_import import (
    ImportResult,
    format_import_result,
    import_groups,
    import_groups_csv,
    import_groups_json,
)


class TestImportGroupsJson:
    def test_basic(self, tmp_path):
        data = [
            {
                "group_id": 0,
                "hash": "abc",
                "file_size": 1000,
                "files": ["/a/file.txt", "/b/file.txt"],
            }
        ]
        path = tmp_path / "groups.json"
        path.write_text(json.dumps(data))
        result = import_groups_json(path)
        assert result.count == 1
        assert result.groups[0].group_id == 0

    def test_nonexistent(self, tmp_path):
        result = import_groups_json(tmp_path / "nope.json")
        assert result.has_errors


class TestImportGroupsCsv:
    def test_basic(self, tmp_path):
        csv_content = "group_id,hash,file_size,wasted_space,count,file_path\n0,abc,1000,1000,2,/a/file.txt\n0,abc,1000,1000,2,/b/file.txt\n"
        path = tmp_path / "groups.csv"
        path.write_text(csv_content)
        result = import_groups_csv(path)
        assert result.count == 1
        assert result.groups[0].count == 2


class TestImportGroups:
    def test_json(self, tmp_path):
        data = [{"group_id": 0, "hash": "abc", "file_size": 100, "files": ["/a"]}]
        path = tmp_path / "groups.json"
        path.write_text(json.dumps(data))
        result = import_groups(path)
        assert result.count == 1

    def test_unsupported(self, tmp_path):
        path = tmp_path / "groups.xml"
        path.write_text("<data/>")
        result = import_groups(path)
        assert result.has_errors


class TestImportResult:
    def test_count(self):
        result = ImportResult()
        assert result.count == 0

    def test_has_errors(self):
        result = ImportResult(errors=["test error"])
        assert result.has_errors is True


class TestFormatImportResult:
    def test_basic(self):
        result = ImportResult(format="json")
        text = format_import_result(result)
        assert "json" in text

    def test_with_errors(self):
        result = ImportResult(format="json", errors=["Parse error"])
        text = format_import_result(result)
        assert "Errors" in text
