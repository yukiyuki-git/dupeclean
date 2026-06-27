"""Tests for DupeClean optimization report module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.models import DuplicateGroup, FileInfo
from dupeclean.opt_report import (
    OptimizationReport,
    Recommendation,
    generate_report,
)


def _fi(path: str, size: int = 100, ext: str = ".txt") -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestRecommendation:
    def test_savings_display(self):
        rec = Recommendation(
            priority=1,
            category="test",
            title="Test",
            description="Desc",
            estimated_savings=1024,
        )
        assert "B" in rec.savings_display


class TestOptimizationReport:
    def test_add(self):
        report = OptimizationReport()
        report.add(Recommendation(priority=2, category="b", title="B", description=""))
        report.add(Recommendation(priority=1, category="a", title="A", description=""))
        assert report.recommendations[0].priority == 1

    def test_total_savings(self):
        report = OptimizationReport()
        report.add(
            Recommendation(
                priority=1, category="a", title="A", description="", estimated_savings=100
            )
        )
        report.add(
            Recommendation(
                priority=2, category="b", title="B", description="", estimated_savings=200
            )
        )
        assert report.total_savings == 300

    def test_render_empty(self):
        report = OptimizationReport()
        assert "No optimization" in report.render()

    def test_render_with_recs(self):
        report = OptimizationReport()
        report.add(
            Recommendation(priority=1, category="dedup", title="Remove dupes", description="Desc")
        )
        text = report.render()
        assert "Remove dupes" in text
        assert "dedup" in text


class TestGenerateReport:
    def test_with_duplicates(self):
        files = [_fi("/a", 100), _fi("/b", 200)]
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/c")],
            )
        ]
        report = generate_report(files, groups)
        assert len(report.recommendations) >= 1

    def test_empty(self):
        report = generate_report([], [])
        # May or may not have recommendations based on file patterns
        assert isinstance(report, OptimizationReport)
