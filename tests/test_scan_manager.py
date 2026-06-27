"""Tests for DupeClean scan manager module."""

from __future__ import annotations

import time

from dupeclean.scan_manager import (
    ScanJob,
    ScanManager,
    format_scan_manager,
)


class TestScanManager:
    def test_create_job(self, tmp_path):
        manager = ScanManager()
        job = manager.create_job(tmp_path)
        assert job.path == tmp_path
        assert manager.total_jobs == 1

    def test_start_job(self, tmp_path):
        manager = ScanManager()
        job = manager.create_job(tmp_path)
        manager.start_job(job)
        assert job.status == "running"

    def test_complete_job(self, tmp_path):
        manager = ScanManager()
        job = manager.create_job(tmp_path)
        manager.start_job(job)
        manager.complete_job(job, 100)
        assert job.status == "completed"
        assert job.files_found == 100

    def test_fail_job(self, tmp_path):
        manager = ScanManager()
        job = manager.create_job(tmp_path)
        manager.start_job(job)
        manager.fail_job(job, "Permission denied")
        assert job.status == "failed"
        assert len(job.errors) == 1

    def test_total_files(self, tmp_path):
        manager = ScanManager()
        j1 = manager.create_job(tmp_path / "a")
        j2 = manager.create_job(tmp_path / "b")
        manager.complete_job(j1, 100)
        manager.complete_job(j2, 200)
        assert manager.total_files == 300

    def test_get_recent(self, tmp_path):
        manager = ScanManager()
        for i in range(20):
            manager.create_job(tmp_path / f"dir_{i}")
        recent = manager.get_recent(5)
        assert len(recent) == 5


class TestScanJob:
    def test_duration(self, tmp_path):
        job = ScanJob(path=tmp_path, start_time=time.time() - 10)
        assert job.duration >= 10


class TestFormatScanManager:
    def test_basic(self, tmp_path):
        manager = ScanManager()
        manager.create_job(tmp_path)
        text = format_scan_manager(manager)
        assert "1 jobs" in text
