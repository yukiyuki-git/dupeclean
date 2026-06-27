"""Tests for DupeClean cleanup history module."""

from __future__ import annotations

import time

import pytest

from dupeclean.history import (
    CleanupHistory,
    CleanupRecord,
    CleanupSession,
    format_history,
)


@pytest.fixture
def sample_session():
    return CleanupSession(
        timestamp=time.time(),
        target="/test",
        records=[
            CleanupRecord(
                timestamp=time.time(),
                action="delete",
                path="/test/dup1.txt",
                size_freed=1000,
                success=True,
            ),
            CleanupRecord(
                timestamp=time.time(),
                action="hardlink",
                path="/test/dup2.txt",
                size_freed=1000,
                success=True,
            ),
        ],
    )


class TestCleanupSession:
    def test_total_freed(self, sample_session):
        assert sample_session.total_freed == 2000

    def test_success_count(self, sample_session):
        assert sample_session.success_count == 2

    def test_error_count(self, sample_session):
        assert sample_session.error_count == 0


class TestCleanupHistory:
    def test_add_session(self, sample_session):
        history = CleanupHistory()
        history.add_session(sample_session)
        assert len(history.sessions) == 1

    def test_total_freed(self, sample_session):
        history = CleanupHistory()
        history.add_session(sample_session)
        assert history.total_freed() == 2000

    def test_total_operations(self, sample_session):
        history = CleanupHistory()
        history.add_session(sample_session)
        assert history.total_operations() == 2

    def test_save_and_load(self, tmp_path, sample_session):
        history = CleanupHistory()
        history.add_session(sample_session)

        save_path = tmp_path / "history.json"
        history.save(save_path)
        assert save_path.exists()

        loaded = CleanupHistory.load(save_path)
        assert len(loaded.sessions) == 1
        assert loaded.total_freed() == 2000

    def test_load_nonexistent(self, tmp_path):
        history = CleanupHistory.load(tmp_path / "nope")
        assert len(history.sessions) == 0

    def test_multiple_sessions(self):
        history = CleanupHistory()
        for i in range(5):
            session = CleanupSession(
                timestamp=time.time(),
                target=f"/test_{i}",
                records=[
                    CleanupRecord(
                        timestamp=time.time(),
                        action="delete",
                        path=f"/test_{i}/file",
                        size_freed=100 * (i + 1),
                    )
                ],
            )
            history.add_session(session)
        assert history.total_operations() == 5


class TestFormatHistory:
    def test_empty(self):
        history = CleanupHistory()
        assert "No cleanup" in format_history(history)

    def test_with_sessions(self, sample_session):
        history = CleanupHistory()
        history.add_session(sample_session)
        text = format_history(history)
        assert "sessions" in text.lower() or "1" in text
