"""Tests for DupeClean cleanup recorder module."""

from __future__ import annotations

from dupeclean.recorder import (
    CleanupRecorder,
    RecordedAction,
    format_recording,
)


class TestCleanupRecorder:
    def test_record(self):
        recorder = CleanupRecorder()
        recorder.record("delete", "/a.txt", size=100)
        assert recorder.total_actions == 1

    def test_success_count(self):
        recorder = CleanupRecorder()
        recorder.record("delete", "/a", success=True)
        recorder.record("delete", "/b", success=False)
        assert recorder.success_count == 1

    def test_total_size(self):
        recorder = CleanupRecorder()
        recorder.record("delete", "/a", size=100, success=True)
        recorder.record("delete", "/b", size=200, success=False)
        assert recorder.total_size == 100

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "recording.json"
        recorder = CleanupRecorder()
        recorder.record("delete", "/a", size=100)
        recorder.save(path)
        assert path.exists()

        loaded = CleanupRecorder.load(path)
        assert loaded.total_actions == 1

    def test_load_nonexistent(self, tmp_path):
        recorder = CleanupRecorder.load(tmp_path / "nope")
        assert recorder.total_actions == 0


class TestRecordedAction:
    def test_size_display(self):
        action = RecordedAction(timestamp=0, action_type="delete", source_path="/a", size=1024)
        assert "B" in action.size_display


class TestFormatRecording:
    def test_empty(self):
        recorder = CleanupRecorder()
        assert "No recorded" in format_recording(recorder)

    def test_with_actions(self):
        recorder = CleanupRecorder()
        recorder.record("delete", "/a", size=100)
        text = format_recording(recorder)
        assert "1 actions" in text
