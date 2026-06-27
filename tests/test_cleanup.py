"""Tests for DupeClean cleanup."""

from pathlib import Path

import pytest

from dupeclean.cleanup import CleanupManager, auto_select_action
from dupeclean.models import CleanupAction, DuplicateGroup, FileInfo


@pytest.fixture
def cleanup_files(tmp_path):
    files = []
    paths = []
    for i in range(3):
        p = tmp_path / f"test_file_{i}.txt"
        p.write_bytes(b"same content " * 100)
        fi = FileInfo.from_path(p)
        if fi:
            files.append(fi)
            paths.append(p)
    return files, paths


class TestCleanupManager:
    def test_dry_run_delete(self, cleanup_files):
        files, paths = cleanup_files
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=files[0].size, files=files)
        manager = CleanupManager(dry_run=True)
        result = manager.execute_cleanup([group], CleanupAction.DELETE)
        assert result.files_processed == 2
        assert result.space_freed > 0
        for p in paths:
            assert p.exists()

    def test_actual_delete(self, cleanup_files):
        files, paths = cleanup_files
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=files[0].size, files=files)
        manager = CleanupManager(dry_run=False)
        result = manager.execute_cleanup([group], CleanupAction.DELETE)
        assert result.files_deleted == 2
        assert paths[0].exists()
        assert not paths[1].exists()
        assert not paths[2].exists()

    def test_keep_newest(self, cleanup_files):
        files, _paths = cleanup_files
        for i, fi in enumerate(files):
            fi.mtime = 100 + i * 10
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=files[0].size, files=files)
        manager = CleanupManager(dry_run=True)
        result = manager.execute_cleanup([group], CleanupAction.KEEP_NEWEST)
        assert result.files_processed == 2

    def test_keep_oldest(self, cleanup_files):
        files, _paths = cleanup_files
        for i, fi in enumerate(files):
            fi.mtime = 100 + i * 10
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=files[0].size, files=files)
        manager = CleanupManager(dry_run=True)
        result = manager.execute_cleanup([group], CleanupAction.KEEP_OLDEST)
        assert result.files_processed == 2

    def test_progress_callback(self, cleanup_files):
        files, _paths = cleanup_files
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=files[0].size, files=files)
        manager = CleanupManager(dry_run=True)
        messages = []
        manager.on_progress(lambda msg, done, total: messages.append(msg))
        manager.execute_cleanup([group], CleanupAction.DELETE)
        assert len(messages) > 0


class TestAutoSelect:
    def test_shortest_path(self):
        files = [
            FileInfo(path=Path("/very/long/nested/path/file.txt"), size=100, mtime=1),
            FileInfo(path=Path("/short/file.txt"), size=100, mtime=2),
            FileInfo(path=Path("/medium/path/file.txt"), size=100, mtime=3),
        ]
        group = DuplicateGroup(group_id=0, hash_value="abc", file_size=100, files=files)
        keep_idx, remove = auto_select_action(group)
        assert keep_idx == 1
        assert remove == [0, 2]
