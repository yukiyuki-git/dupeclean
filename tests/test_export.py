"""Tests for DupeClean file export module."""

from __future__ import annotations

import json

from dupeclean.analyzer import AnalysisResult
from dupeclean.export import (
    export_csv,
    export_json,
    export_summary,
    export_tsv,
)
from dupeclean.models import DirInfo, FileInfo, ScanStats


def _make_result(tmp_path) -> AnalysisResult:
    files = []
    for name, content in [
        ("a.txt", b"hello"),
        ("b.txt", b"hello"),
        ("c.py", b"print('hi')"),
    ]:
        p = tmp_path / name
        p.write_bytes(content)
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)

    dirs = {
        tmp_path: DirInfo(
            path=tmp_path,
            total_size=sum(f.size for f in files),
            file_count=len(files),
        )
    }
    stats = ScanStats(
        total_files=len(files),
        total_dirs=1,
        total_size=sum(f.size for f in files),
        scan_duration=0.1,
    )
    stats.extensions = {"txt": (2, 10), "py": (1, 11)}

    return AnalysisResult(
        root=tmp_path,
        files=files,
        dirs=dirs,
        stats=stats,
        duplicates=[],
    )


class TestExportJson:
    def test_basic(self, tmp_path):
        result = _make_result(tmp_path)
        path = tmp_path / "export.json"
        export_json(result, path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["summary"]["total_files"] == 3

    def test_contains_files(self, tmp_path):
        result = _make_result(tmp_path)
        path = tmp_path / "export.json"
        export_json(result, path)
        data = json.loads(path.read_text())
        assert len(data["files"]) == 3


class TestExportCsv:
    def test_basic(self, tmp_path):
        result = _make_result(tmp_path)
        path = tmp_path / "export.csv"
        export_csv(result, path)
        assert path.exists()
        content = path.read_text()
        assert "path" in content
        assert "size" in content


class TestExportTsv:
    def test_basic(self, tmp_path):
        result = _make_result(tmp_path)
        path = tmp_path / "export.tsv"
        export_tsv(result, path)
        assert path.exists()


class TestExportSummary:
    def test_basic(self, tmp_path):
        result = _make_result(tmp_path)
        path = tmp_path / "summary.txt"
        export_summary(result, path)
        assert path.exists()
        content = path.read_text()
        assert "Directory" in content
