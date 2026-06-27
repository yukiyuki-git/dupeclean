"""Tests for DupeClean state management module."""

from __future__ import annotations

import pytest

from dupeclean.state import (
    DedupState,
    StateManager,
    format_state,
)


@pytest.fixture
def state_manager(tmp_path):
    return StateManager(tmp_path / "states")


class TestDedupState:
    def test_defaults(self):
        state = DedupState(operation_id="test")
        assert state.status == "pending"
        assert state.progress == 0.0

    def test_is_running(self):
        state = DedupState(operation_id="test", status="running")
        assert state.is_running is True

    def test_is_complete(self):
        state = DedupState(operation_id="test", status="completed")
        assert state.is_complete is True

    def test_is_failed(self):
        state = DedupState(operation_id="test", status="failed")
        assert state.is_failed is True

    def test_is_resumable(self):
        state = DedupState(operation_id="test", status="paused")
        assert state.is_resumable is True
        state2 = DedupState(operation_id="test", status="failed")
        assert state2.is_resumable is True


class TestStateManager:
    def test_create(self, state_manager):
        state = state_manager.create("op1")
        assert state.operation_id == "op1"
        assert state.status == "pending"

    def test_get(self, state_manager):
        state_manager.create("op1")
        state = state_manager.get("op1")
        assert state is not None
        assert state.operation_id == "op1"

    def test_get_nonexistent(self, state_manager):
        assert state_manager.get("nope") is None

    def test_update_status(self, state_manager):
        state_manager.create("op1")
        state_manager.update_status("op1", "running")
        state = state_manager.get("op1")
        assert state is not None
        assert state.status == "running"

    def test_update_progress(self, state_manager):
        state_manager.create("op1")
        state_manager.update_progress("op1", 50.0, "hashing")
        state = state_manager.get("op1")
        assert state is not None
        assert state.progress == 50.0
        assert state.stage == "hashing"

    def test_list_operations(self, state_manager):
        state_manager.create("op1")
        state_manager.create("op2")
        ops = state_manager.list_operations()
        assert len(ops) == 2


class TestFormatState:
    def test_basic(self):
        state = DedupState(
            operation_id="test",
            status="running",
            progress=50.0,
        )
        text = format_state(state)
        assert "test" in text
        assert "running" in text
        assert "50.0%" in text
