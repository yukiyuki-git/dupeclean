"""Safe file cleanup operations for DupeClean."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable, Optional

from .models import CleanupAction, CleanupResult, DuplicateGroup, FileInfo
from .utils import create_hardlink, safe_remove


class CleanupManager:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self._cancelled = False
        self._on_progress: Optional[Callable[[str, int, int], None]] = None

    def cancel(self) -> None:
        self._cancelled = True

    def on_progress(self, callback: Callable[[str, int, int], None]) -> None:
        self._on_progress = callback

    def execute_cleanup(self, groups: list[DuplicateGroup], action: CleanupAction, move_dest: Optional[Path] = None) -> CleanupResult:
        result = CleanupResult(action=action)
        self._cancelled = False
        total = sum(g.count - 1 for g in groups)
        processed = 0

        for group in groups:
            if self._cancelled:
                break
            keep_idx = self._choose_keeper(group, action)
            for i, fi in enumerate(group.files):
                if self._cancelled:
                    break
                if i == keep_idx:
                    continue
                processed += 1
                if self._on_progress:
                    self._on_progress(f"Processing: {fi.path.name}", processed, total)
                if self.dry_run:
                    result.files_processed += 1
                    result.space_freed += fi.size
                    continue
                success, error = self._apply_action(fi, action, group.files[keep_idx], move_dest)
                result.files_processed += 1
                if success:
                    result.files_deleted += 1
                    result.space_freed += fi.size
                    if action == CleanupAction.HARDLINK:
                        result.hardlinks_created += 1
                elif error:
                    result.errors.append(error)
        return result

    def _choose_keeper(self, group: DuplicateGroup, action: CleanupAction) -> int:
        if action == CleanupAction.KEEP_NEWEST:
            return max(range(group.count), key=lambda i: group.files[i].mtime)
        if action == CleanupAction.KEEP_OLDEST:
            return min(range(group.count), key=lambda i: group.files[i].mtime)
        if action == CleanupAction.KEEP_SHORTEST_PATH:
            return min(range(group.count), key=lambda i: len(str(group.files[i].path)))
        return 0

    def _apply_action(self, fi: FileInfo, action: CleanupAction, keeper: FileInfo, move_dest: Optional[Path]) -> tuple[bool, str]:
        if action in (CleanupAction.DELETE, CleanupAction.KEEP_NEWEST, CleanupAction.KEEP_OLDEST, CleanupAction.KEEP_SHORTEST_PATH):
            return safe_remove(fi.path)
        if action == CleanupAction.RECYCLE:
            return self._recycle(fi.path)
        if action == CleanupAction.HARDLINK:
            return create_hardlink(keeper.path, fi.path)
        if action == CleanupAction.MOVE:
            return self._move(fi.path, move_dest)
        return False, f"Unknown action: {action}"

    def _recycle(self, path: Path) -> tuple[bool, str]:
        try:
            from send2trash import send2trash
            send2trash(str(path))
            return True, ""
        except ImportError:
            trash_dir = path.parent / ".dupeclean_trash"
            trash_dir.mkdir(exist_ok=True)
            try:
                dest = trash_dir / path.name
                counter = 1
                while dest.exists():
                    dest = trash_dir / f"{path.stem}_{counter}{path.suffix}"
                    counter += 1
                shutil.move(str(path), str(dest))
                return True, ""
            except OSError as e:
                return False, f"Failed to move to trash: {e}"
        except Exception as e:
            return False, f"Failed to recycle: {e}"

    def _move(self, path: Path, dest: Optional[Path]) -> tuple[bool, str]:
        if dest is None:
            return False, "No destination specified for move"
        try:
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / path.name
            counter = 1
            while target.exists():
                target = dest / f"{path.stem}_{counter}{path.suffix}"
                counter += 1
            shutil.move(str(path), str(target))
            return True, ""
        except OSError as e:
            return False, f"Failed to move: {e}"


def auto_select_action(group: DuplicateGroup) -> tuple[int, list[int]]:
    if not group.files:
        return -1, []
    keep_idx = min(range(group.count), key=lambda i: len(str(group.files[i].path)))
    remove = [i for i in range(group.count) if i != keep_idx]
    return keep_idx, remove
