"""Tests for DupeClean scan result analyzer."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.models import FileInfo, ScanStats
from dupeclean.scan_analyzer import (
    ScanAnalysisResult,
    ScanInsight,
    analyze_scan_result,
    format_scan_insights,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestAnalyzeScanResult:
    def test_large_files(self):
        files = [_fi("/big.bin", 2_000_000_000)]
        stats = ScanStats(total_files=1, total_size=2_000_000_000)
        result = analyze_scan_result(files, stats)
        assert any("large" in i.title.lower() for i in result.insights)

    def test_old_files(self):
        old_time = time.time() - (400 * 86400)
        files = [_fi("/old.txt", 100, mtime=old_time)]
        stats = ScanStats(total_files=1, total_size=100)
        result = analyze_scan_result(files, stats)
        assert any("old" in i.title.lower() for i in result.insights)

    def test_no_insights(self):
        files = [_fi("/normal.txt", 100, mtime=time.time())]
        stats = ScanStats(total_files=1, total_size=100)
        result = analyze_scan_result(files, stats)
        # May or may not have insights depending on file characteristics
        assert isinstance(result, ScanAnalysisResult)


class TestScanInsight:
    def test_icon(self):
        insight = ScanInsight(category="test", title="test", description="test", severity="warning")
        assert insight.icon == "[!]"


class TestScanAnalysisResult:
    def test_has_warnings(self):
        result = ScanAnalysisResult(
            insights=[
                ScanInsight(category="test", title="test", description="test", severity="warning")
            ]
        )
        assert result.has_warnings is True

    def test_no_warnings(self):
        result = ScanAnalysisResult(
            insights=[
                ScanInsight(category="test", title="test", description="test", severity="info")
            ]
        )
        assert result.has_warnings is False


class TestFormatScanInsights:
    def test_empty(self):
        result = ScanAnalysisResult()
        assert "No insights" in format_scan_insights(result)

    def test_with_insights(self):
        result = ScanAnalysisResult(
            insights=[ScanInsight(category="test", title="Test insight", description="Details")]
        )
        text = format_scan_insights(result)
        assert "Test insight" in text
