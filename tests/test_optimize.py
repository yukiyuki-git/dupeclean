"""Tests for DupeClean file optimization module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.optimize import (
    Optimization,
    OptimizationPlan,
    create_optimization_plan,
    find_archive_candidates,
    find_compression_candidates,
    find_temp_files,
    format_optimization_plan,
)


def _fi(path: str, size: int = 10000, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestFindCompressionCandidates:
    def test_compressible_files(self):
        files = [
            _fi("/code.py", 50000),
            _fi("/data.json", 100000),
            _fi("/image.jpg", 500000),
        ]
        results = find_compression_candidates(files, min_size=10000)
        assert len(results) == 2  # .py and .json
        assert all(o.action == "compress" for o in results)

    def test_small_files_excluded(self):
        files = [_fi("/tiny.txt", 100)]
        results = find_compression_candidates(files, min_size=1000)
        assert len(results) == 0


class TestFindArchiveCandidates:
    def test_old_files(self):
        old_time = time.time() - (400 * 86400)
        files = [
            _fi("/old.txt", 1000, mtime=old_time),
            _fi("/new.txt", 1000, mtime=time.time()),
        ]
        results = find_archive_candidates(files, max_age_days=365)
        assert len(results) == 1


class TestFindTempFiles:
    def test_temp_files(self):
        files = [
            _fi("/data.tmp", 1000),
            _fi("/backup.bak", 2000),
            _fi("/normal.txt", 3000),
        ]
        results = find_temp_files(files)
        assert len(results) == 2


class TestCreateOptimizationPlan:
    def test_basic(self):
        now = time.time()
        old_time = now - (400 * 86400)
        files = [
            _fi("/code.py", 50000, mtime=now),
            _fi("/old.txt", 10000, mtime=old_time),
            _fi("/temp.tmp", 5000, mtime=now),
        ]
        plan = create_optimization_plan(files)
        assert plan.count >= 2
        assert plan.total_savings > 0


class TestOptimizationPlan:
    def test_total_savings(self):
        plan = OptimizationPlan(
            optimizations=[
                Optimization(
                    file=_fi("/a", 1000),
                    action="compress",
                    reason="test",
                    estimated_savings=600,
                ),
                Optimization(
                    file=_fi("/b", 2000),
                    action="compress",
                    reason="test",
                    estimated_savings=1200,
                ),
            ]
        )
        assert plan.total_savings == 1800


class TestFormatOptimizationPlan:
    def test_empty(self):
        plan = OptimizationPlan()
        assert "No optimizations" in format_optimization_plan(plan)

    def test_with_optimizations(self):
        plan = OptimizationPlan(
            optimizations=[
                Optimization(
                    file=_fi("/code.py", 50000),
                    action="compress",
                    reason="Text file",
                    estimated_savings=30000,
                ),
            ]
        )
        text = format_optimization_plan(plan)
        assert "COMPRESS" in text
