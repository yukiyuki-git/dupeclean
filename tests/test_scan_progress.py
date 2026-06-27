"""Tests for DupeClean scan progress module."""

from __future__ import annotations

import time

from dupeclean.scan_progress import (
    ScanProgress,
    create_scan_progress,
)


class TestScanProgress:
    def test_dir_percentage(self):
        progress = ScanProgress(total_dirs=100, dirs_scanned=50)
        assert progress.dir_percentage == 50.0

    def test_file_percentage(self):
        progress = ScanProgress(total_files=100, files_scanned=50)
        assert progress.file_percentage == 50.0

    def test_update(self):
        progress = ScanProgress(total_files=100)
        progress.update(files=10, dirs=5, bytes_count=1024)
        assert progress.files_scanned == 10
        assert progress.dirs_scanned == 5
        assert progress.bytes_scanned == 1024

    def test_eta_none(self):
        progress = ScanProgress(total_files=100, files_scanned=0)
        assert progress.eta_seconds is None

    def test_mb_scanned(self):
        progress = ScanProgress(bytes_scanned=1048576)
        assert "B" in progress.mb_scanned

    def test_render(self):
        progress = ScanProgress(
            total_files=100,
            files_scanned=50,
            start_time=time.monotonic(),
        )
        text = progress.render()
        assert "50.0%" in text


class TestCreateScanProgress:
    def test_basic(self):
        progress = create_scan_progress(1000, 50)
        assert progress.total_files == 1000
        assert progress.total_dirs == 50
        assert progress.start_time > 0
