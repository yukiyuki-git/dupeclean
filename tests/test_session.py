"""Tests for DupeClean session module."""

from __future__ import annotations

from dupeclean.session import (
    CleanupSession,
    SessionState,
    format_session,
)


class TestCleanupSession:
    def test_start(self):
        session = CleanupSession("test")
        session.start()
        assert session.state.status == "scanning"
        assert session.state.start_time > 0

    def test_set_status(self):
        session = CleanupSession("test")
        session.start()
        session.set_status("analyzing")
        assert session.state.status == "analyzing"

    def test_record_scan(self):
        session = CleanupSession("test")
        session.record_scan(100)
        assert session.state.files_scanned == 100

    def test_record_groups(self):
        session = CleanupSession("test")
        session.record_groups(5)
        assert session.state.groups_found == 5

    def test_record_cleanup(self):
        session = CleanupSession("test")
        session.record_cleanup(10, 1000)
        session.record_cleanup(5, 500)
        assert session.state.files_cleaned == 15
        assert session.state.space_freed == 1500

    def test_record_error(self):
        session = CleanupSession("test")
        session.record_error("Permission denied")
        assert len(session.state.errors) == 1

    def test_complete(self):
        session = CleanupSession("test")
        session.start()
        session.complete()
        assert session.state.status == "done"
        assert session.state.end_time > 0

    def test_events(self):
        session = CleanupSession("test")
        session.start()
        session.record_scan(100)
        assert len(session.events) >= 2


class TestSessionState:
    def test_elapsed(self):
        state = SessionState(session_id="test")
        assert state.elapsed == 0.0

    def test_freed_display(self):
        state = SessionState(session_id="test", space_freed=1024)
        assert "B" in state.freed_display


class TestFormatSession:
    def test_basic(self):
        session = CleanupSession("test")
        session.start()
        session.record_scan(100)
        text = format_session(session)
        assert "test" in text
        assert "100" in text
