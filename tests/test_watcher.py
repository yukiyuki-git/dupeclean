"""Tests for DupeClean directory watcher."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.watcher import (
    DirectoryWatcher,
    FileEvent,
    WatchState,
)


class TestFileEvent:
    def test_display_created(self):
        event = FileEvent(
            event_type="created", path=Path("/test/file.txt")
        )
        assert "CREATED" in event.display

    def test_display_renamed(self):
        event = FileEvent(
            event_type="renamed",
            path=Path("/test/new.txt"),
            old_path=Path("/test/old.txt"),
        )
        assert "RENAMED" in event.display
        assert "old.txt" in event.display


class TestDirectoryWatcher:
    def test_initial_scan(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")

        watcher = DirectoryWatcher(tmp_path)
        state = watcher._scan()

        assert len(state.files) == 2

    def test_detect_new_file(self, tmp_path):
        (tmp_path / "existing.txt").write_text("hello")

        watcher = DirectoryWatcher(tmp_path)
        old_state = watcher._scan()

        (tmp_path / "new.txt").write_text("new file")
        new_state = watcher._scan()

        events = watcher._compare(old_state, new_state)
        assert len(events) == 1
        assert events[0].event_type == "created"
        assert events[0].path.name == "new.txt"

    def test_detect_deleted_file(self, tmp_path):
        (tmp_path / "keep.txt").write_text("stay")
        (tmp_path / "delete.txt").write_text("go")

        watcher = DirectoryWatcher(tmp_path)
        old_state = watcher._scan()

        (tmp_path / "delete.txt").unlink()
        new_state = watcher._scan()

        events = watcher._compare(old_state, new_state)
        assert len(events) == 1
        assert events[0].event_type == "deleted"

    def test_detect_modified_file(self, tmp_path):
        f = tmp_path / "modify.txt"
        f.write_text("version 1")

        watcher = DirectoryWatcher(tmp_path)
        old_state = watcher._scan()

        time.sleep(0.01)  # Ensure mtime changes
        f.write_text("version 2 modified")
        new_state = watcher._scan()

        events = watcher._compare(old_state, new_state)
        assert len(events) == 1
        assert events[0].event_type == "modified"

    def test_ignore_patterns(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")
        (tmp_path / "real.txt").write_text("real")

        watcher = DirectoryWatcher(
            tmp_path, ignore_patterns=[".git"]
        )
        state = watcher._scan()

        assert len(state.files) == 1
        assert "real.txt" in next(iter(state.files.keys()))

    def test_no_changes(self, tmp_path):
        (tmp_path / "stable.txt").write_text("no change")

        watcher = DirectoryWatcher(tmp_path)
        old_state = watcher._scan()
        new_state = watcher._scan()

        events = watcher._compare(old_state, new_state)
        assert len(events) == 0

    def test_on_event_callback(self, tmp_path):
        events_received: list[FileEvent] = []
        watcher = DirectoryWatcher(tmp_path)
        watcher.on_event(lambda e: events_received.append(e))

        old_state = WatchState()
        (tmp_path / "new.txt").write_text("new")
        new_state = watcher._scan()

        events = watcher._compare(old_state, new_state)
        for event in events:
            watcher._emit(event)

        assert len(events_received) == 1

    def test_multiple_changes(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")

        watcher = DirectoryWatcher(tmp_path)
        old_state = watcher._scan()

        (tmp_path / "a.txt").unlink()
        (tmp_path / "c.txt").write_text("c")
        (tmp_path / "b.txt").write_text("b modified")

        new_state = watcher._scan()
        events = watcher._compare(old_state, new_state)

        types = {e.event_type for e in events}
        assert "deleted" in types
        assert "created" in types
        assert "modified" in types
