"""Tests for DupeClean report generator."""
import json
from pathlib import Path
import pytest
from dupeclean.analyzer import AnalysisResult
from dupeclean.models import DuplicateGroup, FileInfo, ScanStats, DirInfo
from dupeclean.report import ReportGenerator


@pytest.fixture
def analysis_result(tmp_path):
    files = []
    for name, content in [("a.txt", b"hello"), ("b.txt", b"hello"), ("c.py", b"print('hi')")]:
        p = tmp_path / name
        p.write_bytes(content)
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)
    dirs = {tmp_path: DirInfo(path=tmp_path, total_size=sum(f.size for f in files), file_count=len(files))}
    stats = ScanStats(total_files=len(files), total_dirs=1, total_size=sum(f.size for f in files), scan_duration=0.5, duplicate_groups=1, duplicate_files=2, wasted_space=5)
    stats.extensions = {"txt": (2, 10), "py": (1, 11)}
    dup_group = DuplicateGroup(group_id=0, hash_value="abc123", file_size=5, files=[files[0], files[1]])
    return AnalysisResult(root=tmp_path, files=files, dirs=dirs, stats=stats, duplicates=[dup_group])


class TestReportGenerator:
    def test_json_report(self, analysis_result):
        gen = ReportGenerator(analysis_result)
        content = gen.generate("json")
        assert content is not None
        data = json.loads(content)
        assert "summary" in data
        assert data["summary"]["total_files"] == 3

    def test_json_report_to_file(self, analysis_result, tmp_path):
        output = tmp_path / "report.json"
        gen = ReportGenerator(analysis_result)
        gen.generate("json", output)
        assert output.exists()

    def test_csv_report(self, analysis_result):
        gen = ReportGenerator(analysis_result)
        content = gen.generate("csv")
        assert content is not None
        lines = content.strip().split("\n")
        assert len(lines) >= 3

    def test_html_report(self, analysis_result):
        gen = ReportGenerator(analysis_result)
        content = gen.generate("html")
        assert content is not None
        assert "<!DOCTYPE html>" in content

    def test_unknown_format(self, analysis_result):
        gen = ReportGenerator(analysis_result)
        content = gen.generate("xml")
        assert content is None
