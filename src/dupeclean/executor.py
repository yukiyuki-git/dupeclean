"""File deduplication cleanup executor for DupeClean.

Execute cleanup operations with safety and rollback support.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .models import format_size
from .utils import create_hardlink, safe_remove


@dataclass
class ExecutorAction:
    """An action to execute."""

    action_type: str
    source: Path
    target: Path | None = None
    size: int = 0

    @property
    def size_display(self) -> str:
        return format_size(self.size)


@dataclass
class ExecutorResult:
    """Result of executing an action."""

    action: ExecutorAction
    success: bool
    error: str = ""
    backup_path: Path | None = None


@dataclass
class CleanupExecutorV2:
    """Execute cleanup with backup and rollback."""

    dry_run: bool = True
    backup_dir: Path | None = None
    results: list[ExecutorResult] = field(default_factory=list)
    backups: dict[str, Path] = field(default_factory=dict)  # original_path -> backup_path

    def execute(self, action: ExecutorAction) -> ExecutorResult:
        """Execute a single action with backup."""
        if self.dry_run:
            result = ExecutorResult(action=action, success=True)
            self.results.append(result)
            return result

        # Create backup if needed
        backup_path = None
        if action.action_type == "delete" and action.source.exists():
            backup_path = self._create_backup(action.source)

        success = False
        error = ""

        if action.action_type == "delete":
            success, error = safe_remove(action.source)
        elif action.action_type == "hardlink" and action.target:
            success, error = create_hardlink(action.target, action.source)

        # Remove backup on success
        if success and backup_path and backup_path.exists():
            backup_path.unlink()
            backup_path = None

        # Restore from backup on failure
        if not success and backup_path and backup_path.exists():
            shutil.move(str(backup_path), str(action.source))
            backup_path = None

        result = ExecutorResult(
            action=action,
            success=success,
            error=error,
            backup_path=backup_path,
        )
        self.results.append(result)
        return result

    def _create_backup(self, path: Path) -> Path | None:
        """Create a backup of a file."""
        if not self.backup_dir:
            return None
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup = self.backup_dir / f"{path.name}.bak"
            shutil.copy2(str(path), str(backup))
            return backup
        except OSError:
            return None

    def rollback(self) -> int:
        """Rollback all successful actions. Returns count restored."""
        restored = 0
        for result in reversed(self.results):
            if result.success and result.backup_path and result.backup_path.exists():
                try:
                    shutil.move(str(result.backup_path), str(result.action.source))
                    restored += 1
                except OSError:
                    pass
        return restored

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def total_freed(self) -> int:
        return sum(r.action.size for r in self.results if r.success)


def format_executor_result(result: ExecutorResult) -> str:
    """Format executor result as text."""
    status = "OK" if result.success else "FAILED"
    return (
        f"[{status}] {result.action.action_type}: "
        f"{result.action.source.name} ({result.action.size_display})"
    )
