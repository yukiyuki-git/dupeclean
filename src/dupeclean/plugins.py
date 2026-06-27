"""Plugin system for DupeClean.

Allows extending DupeClean with custom analysis plugins.
Plugins are Python modules that register hooks for various
scan lifecycle events.
"""

from __future__ import annotations

import importlib
import importlib.util
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import DuplicateGroup, FileInfo, ScanStats


@dataclass
class PluginInfo:
    """Registered plugin information."""
    name: str
    version: str
    description: str
    hooks: dict[str, Callable] = field(default_factory=dict)


class PluginManager:
    """Manages DupeClean plugins.

    Plugins can hook into:
    - on_scan_start: Before scanning begins
    - on_file_found: When a file is discovered
    - on_scan_complete: After scanning finishes
    - on_duplicates_found: After duplicates are detected
    - on_report: When generating reports
    """

    HOOK_NAMES = [
        "on_scan_start",
        "on_file_found",
        "on_scan_complete",
        "on_duplicates_found",
        "on_report",
    ]

    def __init__(self) -> None:
        self._plugins: dict[str, PluginInfo] = {}
        self._hooks: dict[str, list[Callable]] = {
            h: [] for h in self.HOOK_NAMES
        }

    def register(self, plugin: PluginInfo) -> None:
        """Register a plugin."""
        self._plugins[plugin.name] = plugin
        for hook_name, callback in plugin.hooks.items():
            if hook_name in self._hooks:
                self._hooks[hook_name].append(callback)

    def unregister(self, name: str) -> None:
        """Unregister a plugin by name."""
        import contextlib

        if name in self._plugins:
            plugin = self._plugins.pop(name)
            for hook_name, callback in plugin.hooks.items():
                if hook_name in self._hooks:
                    with contextlib.suppress(ValueError):
                        self._hooks[hook_name].remove(callback)

    def load_plugin(self, module_path: Path) -> bool:
        """Load a plugin from a Python file.

        The module should define a `register(manager)` function.
        """
        try:
            spec = importlib.util.spec_from_file_location(
                f"dupeclean_plugin_{module_path.stem}",
                str(module_path),
            )
            if spec is None or spec.loader is None:
                return False
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                module.register(self)
                return True
            return False
        except Exception:
            return False

    def load_plugins_from_dir(self, directory: Path) -> int:
        """Load all plugins from a directory.

        Returns count of successfully loaded plugins.
        """
        loaded = 0
        if not directory.exists():
            return 0

        for py_file in directory.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            if self.load_plugin(py_file):
                loaded += 1

        return loaded

    @property
    def plugins(self) -> dict[str, PluginInfo]:
        return dict(self._plugins)

    @property
    def plugin_count(self) -> int:
        return len(self._plugins)

    def fire(
        self, hook_name: str, **kwargs: Any
    ) -> list[Any]:
        """Fire a hook and collect results.

        Returns list of non-None return values from hooks.
        """
        results: list[Any] = []
        for callback in self._hooks.get(hook_name, []):
            try:
                result = callback(**kwargs)
                if result is not None:
                    results.append(result)
            except Exception:
                pass  # Don't let plugin errors crash the scan
        return results

    def fire_on_scan_start(self, path: Path) -> list[Any]:
        return self.fire("on_scan_start", path=path)

    def fire_on_file_found(self, fi: FileInfo) -> list[Any]:
        return self.fire("on_file_found", file_info=fi)

    def fire_on_scan_complete(
        self, stats: ScanStats
    ) -> list[Any]:
        return self.fire("on_scan_complete", stats=stats)

    def fire_on_duplicates_found(
        self, groups: list[DuplicateGroup]
    ) -> list[Any]:
        return self.fire("on_duplicates_found", groups=groups)


# Built-in plugin: scan summary
def _summary_plugin(
    stats: ScanStats,
) -> dict:
    """Built-in plugin that summarizes scan results."""
    return {
        "files": stats.total_files,
        "dirs": stats.total_dirs,
        "size": stats.total_size,
        "dupes": stats.duplicate_groups,
    }


def create_builtin_plugins() -> list[PluginInfo]:
    """Create built-in plugin info."""
    return [
        PluginInfo(
            name="summary",
            version="1.0.0",
            description="Scan summary plugin",
            hooks={"on_scan_complete": _summary_plugin},
        ),
    ]
