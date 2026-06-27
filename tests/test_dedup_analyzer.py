"""Tests for DupeClean dedup analyzer module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.dedup_analyzer import (
    DedupAnalysis,
    analyze_dedup_potential,
    format_dedup_analysis,
)
from dupeclean.models import DuplicateGroup, FileInfo, ScanStats


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestAnalyzeDedupPotential:
    def test_basic(self):
        files = [
            _fi("/a", 100),
            _fi("/b", 100),
            _fi("/c", 200),
            _fi("/d", 200),
            _fi("/e", 200),
        ]
        stats = ScanStats(total_files=5, total_size=800)
        result = analyze_dedup_potential(files, stats)
        assert len(result.size_groups) == 2

    def test_no_duplicates(self):
        files = [_fi("/a", 100), _fi("/b", 200), _fi("/c", 300)]
        stats = ScanStats(total_files=3, total_size=600)
        result = analyze_dedup_potential(files, stats)
        assert len(result.size_groups) == 0

    def test_empty_files(self):
        files = [_fi("/a", 0), _fi("/b", 0)]
        stats = ScanStats()
        result = analyze_dedup_potential(files, stats)
        assert len(result.size_groups) == 0  # Size 0 skipped


class TestDedupAnalysis:
    def test_total_duplicates(self):
        analysis = DedupAnalysis(
            scan_stats=ScanStats(),
            exact_groups=[
                DuplicateGroup(
                    group_id=0,
                    hash_value="a",
                    file_size=100,
                    files=[_fi("/a"), _fi("/b")],
                ),
                DuplicateGroup(
                    group_id=1,
                    hash_value="b",
                    file_size=200,
                    files=[_fi("/c"), _fi("/d"), _fi("/e")],
                ),
            ],
        )
        assert analysis.total_duplicates == 5

    def test_total_wasted(self):
        analysis = DedupAnalysis(
            scan_stats=ScanStats(),
            exact_groups=[
                DuplicateGroup(
                    group_id=0,
                    hash_value="a",
                    file_size=1000,
                    files=[_fi("/a"), _fi("/b")],
                ),
            ],
        )
        assert analysis.total_wasted == 1000

    def test_savings_display(self):
        analysis = DedupAnalysis(
            scan_stats=ScanStats(),
            exact_groups=[
                DuplicateGroup(
                    group_id=0,
                    hash_value="a",
                    file_size=1024,
                    files=[_fi("/a"), _fi("/b")],
                ),
            ],
        )
        assert "B" in analysis.savings_display


class TestFormatDedupAnalysis:
    def test_basic(self):
        files = [_fi("/a", 100), _fi("/b", 100)]
        stats = ScanStats(total_files=2, total_size=200)
        analysis = analyze_dedup_potential(files, stats)
        text = format_dedup_analysis(analysis)
        assert "Files" in text
        assert "Size-based" in text
