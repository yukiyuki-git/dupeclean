"""File deduplication group tracker for DupeClean.

Track changes to duplicate groups over time.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .models import DuplicateGroup, format_size


@dataclass
class GroupSnapshot:
    """A snapshot of group state."""

    timestamp: float
    group_count: int
    total_wasted: int
    groups: list[dict] = field(default_factory=list)


@dataclass
class GroupTracker:
    """Track group changes over time."""

    snapshots: list[GroupSnapshot] = field(default_factory=list)

    def snapshot(self, groups: list[DuplicateGroup]) -> None:
        """Take a snapshot of current groups."""
        self.snapshots.append(
            GroupSnapshot(
                timestamp=time.time(),
                group_count=len(groups),
                total_wasted=sum(g.wasted_space for g in groups),
                groups=[{"id": g.group_id, "count": g.count, "size": g.file_size} for g in groups],
            )
        )

    @property
    def snapshot_count(self) -> int:
        return len(self.snapshots)

    def get_latest(self) -> GroupSnapshot | None:
        if self.snapshots:
            return self.snapshots[-1]
        return None

    def get_trend(self) -> str:
        """Get trend description."""
        if len(self.snapshots) < 2:
            return "Insufficient data"
        latest = self.snapshots[-1]
        previous = self.snapshots[-2]
        if latest.total_wasted > previous.total_wasted:
            return "Worsening"
        elif latest.total_wasted < previous.total_wasted:
            return "Improving"
        return "Stable"

    def save(self, path: Path) -> None:
        """Save tracker to file."""
        data = [
            {
                "timestamp": s.timestamp,
                "group_count": s.group_count,
                "total_wasted": s.total_wasted,
                "groups": s.groups,
            }
            for s in self.snapshots
        ]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> GroupTracker:
        """Load tracker from file."""
        tracker = cls()
        if not path.exists():
            return tracker
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                tracker.snapshots.append(
                    GroupSnapshot(
                        timestamp=entry["timestamp"],
                        group_count=entry["group_count"],
                        total_wasted=entry["total_wasted"],
                        groups=entry.get("groups", []),
                    )
                )
        except (json.JSONDecodeError, OSError):
            pass
        return tracker


def format_tracker(tracker: GroupTracker) -> str:
    """Format tracker as text."""
    if not tracker.snapshots:
        return "No snapshots recorded."

    latest = tracker.get_latest()
    if latest is None:
        return "No snapshots."

    import datetime

    dt = datetime.datetime.fromtimestamp(latest.timestamp)
    return (
        f"Group Tracker: {tracker.snapshot_count} snapshots\n"
        f"  Latest: {dt.strftime('%Y-%m-%d %H:%M')}\n"
        f"  Groups: {latest.group_count}\n"
        f"  Wasted: {format_size(latest.total_wasted)}\n"
        f"  Trend: {tracker.get_trend()}"
    )
