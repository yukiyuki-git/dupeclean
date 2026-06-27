"""File deduplication state management for DupeClean.

Manage dedup operation state for resumable operations.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DedupState:
    """State of a dedup operation."""
    operation_id: str
    status: str = "pending"  # pending, running, paused, completed, failed
    stage: str = ""
    progress: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    files_processed: int = 0
    total_files: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def is_running(self) -> bool:
        return self.status == "running"

    @property
    def is_complete(self) -> bool:
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    @property
    def is_resumable(self) -> bool:
        return self.status in ("paused", "failed")

    @property
    def elapsed(self) -> float:
        if self.start_time == 0:
            return 0.0
        end = self.end_time if self.end_time > 0 else time.time()
        return end - self.start_time


class StateManager:
    """Manage dedup operation states."""

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def create(self, operation_id: str) -> DedupState:
        """Create a new operation state."""
        state = DedupState(
            operation_id=operation_id,
            status="pending",
            start_time=time.time(),
        )
        self.save(state)
        return state

    def get(self, operation_id: str) -> DedupState | None:
        """Get state by operation ID."""
        path = self._state_path(operation_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return DedupState(**data)
        except (json.JSONDecodeError, OSError):
            return None

    def save(self, state: DedupState) -> None:
        """Save state to file."""
        path = self._state_path(state.operation_id)
        data = {
            "operation_id": state.operation_id,
            "status": state.status,
            "stage": state.stage,
            "progress": state.progress,
            "start_time": state.start_time,
            "end_time": state.end_time,
            "files_processed": state.files_processed,
            "total_files": state.total_files,
            "errors": state.errors,
            "metadata": state.metadata,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def update_status(self, operation_id: str, status: str) -> None:
        """Update operation status."""
        state = self.get(operation_id)
        if state:
            state.status = status
            if status == "completed":
                state.end_time = time.time()
                state.progress = 100.0
            self.save(state)

    def update_progress(
        self,
        operation_id: str,
        progress: float,
        stage: str = "",
    ) -> None:
        """Update operation progress."""
        state = self.get(operation_id)
        if state:
            state.progress = progress
            if stage:
                state.stage = stage
            self.save(state)

    def list_operations(self) -> list[DedupState]:
        """List all tracked operations."""
        states = []
        for path in self.state_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                states.append(DedupState(**data))
            except (json.JSONDecodeError, OSError):
                continue
        return states

    def _state_path(self, operation_id: str) -> Path:
        return self.state_dir / f"{operation_id}.json"


def format_state(state: DedupState) -> str:
    """Format state as text."""
    import datetime

    start = (
        datetime.datetime.fromtimestamp(state.start_time).strftime("%H:%M:%S")
        if state.start_time > 0
        else "N/A"
    )
    elapsed = f"{state.elapsed:.1f}s" if state.elapsed > 0 else "N/A"

    return (
        f"Operation: {state.operation_id}\n"
        f"  Status: {state.status}\n"
        f"  Stage: {state.stage or 'N/A'}\n"
        f"  Progress: {state.progress:.1f}%\n"
        f"  Files: {state.files_processed}/{state.total_files}\n"
        f"  Started: {start}\n"
        f"  Elapsed: {elapsed}\n"
        f"  Errors: {len(state.errors)}"
    )
