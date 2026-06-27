"""File deduplication scanner manager for DupeClean.

Manage and coordinate file scanning operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScanJob:
    """A scan job."""

    path: Path
    status: str = "pending"  # pending, running, completed, failed
    start_time: float = 0.0
    end_time: float = 0.0
    files_found: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        if self.start_time == 0:
            return 0.0
        end = self.end_time if self.end_time > 0 else time.time()
        return end - self.start_time


@dataclass
class ScanManager:
    """Manage scanning operations."""

    jobs: list[ScanJob] = field(default_factory=list)

    def create_job(self, path: Path) -> ScanJob:
        """Create a new scan job."""
        job = ScanJob(path=path)
        self.jobs.append(job)
        return job

    def start_job(self, job: ScanJob) -> None:
        """Start a scan job."""
        job.status = "running"
        job.start_time = time.time()

    def complete_job(self, job: ScanJob, files_found: int) -> None:
        """Complete a scan job."""
        job.status = "completed"
        job.end_time = time.time()
        job.files_found = files_found

    def fail_job(self, job: ScanJob, error: str) -> None:
        """Mark a scan job as failed."""
        job.status = "failed"
        job.end_time = time.time()
        job.errors.append(error)

    @property
    def total_jobs(self) -> int:
        return len(self.jobs)

    @property
    def completed_jobs(self) -> int:
        return sum(1 for j in self.jobs if j.status == "completed")

    @property
    def total_files(self) -> int:
        return sum(j.files_found for j in self.jobs)

    def get_recent(self, count: int = 10) -> list[ScanJob]:
        """Get recent scan jobs."""
        return self.jobs[-count:]


def format_scan_manager(manager: ScanManager) -> str:
    """Format scan manager as text."""
    return (
        f"Scan Manager: {manager.total_jobs} jobs "
        f"({manager.completed_jobs} completed), "
        f"{manager.total_files:,} files found"
    )
