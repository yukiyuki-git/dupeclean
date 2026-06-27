"""Tests for DupeClean plugin system."""

from __future__ import annotations

from pathlib import Path

import pytest

from dupeclean.models import ScanStats
from dupeclean.plugins import (
    PluginInfo,
    PluginManager,
    create_builtin_plugins,
)


@pytest.fixture
def manager():
    return PluginManager()


class TestPluginManager:
    def test_register_plugin(self, manager):
        plugin = PluginInfo(
            name="test",
            version="1.0.0",
            description="Test plugin",
        )
        manager.register(plugin)
        assert manager.plugin_count == 1
        assert "test" in manager.plugins

    def test_unregister_plugin(self, manager):
        plugin = PluginInfo(
            name="test",
            version="1.0.0",
            description="Test plugin",
        )
        manager.register(plugin)
        manager.unregister("test")
        assert manager.plugin_count == 0

    def test_unregister_unknown(self, manager):
        manager.unregister("nonexistent")
        assert manager.plugin_count == 0

    def test_fire_hook(self, manager):
        results = []

        def on_start(path):
            results.append(str(path))

        plugin = PluginInfo(
            name="test",
            version="1.0",
            description="test",
            hooks={"on_scan_start": on_start},
        )
        manager.register(plugin)
        manager.fire_on_scan_start(Path("/test"))

        assert len(results) == 1
        assert Path(results[0]) == Path("/test")

    def test_fire_hook_with_return(self, manager):
        def on_complete(stats):
            return {"files": stats.total_files}

        plugin = PluginInfo(
            name="test",
            version="1.0",
            description="test",
            hooks={"on_scan_complete": on_complete},
        )
        manager.register(plugin)

        stats = ScanStats(total_files=42)
        results = manager.fire_on_scan_complete(stats)

        assert len(results) == 1
        assert results[0]["files"] == 42

    def test_multiple_hooks(self, manager):
        count = {"a": 0, "b": 0}

        def hook_a(path):
            count["a"] += 1

        def hook_b(path):
            count["b"] += 1

        manager.register(
            PluginInfo(
                name="a",
                version="1.0",
                description="a",
                hooks={"on_scan_start": hook_a},
            )
        )
        manager.register(
            PluginInfo(
                name="b",
                version="1.0",
                description="b",
                hooks={"on_scan_start": hook_b},
            )
        )

        manager.fire_on_scan_start(Path("/test"))
        assert count["a"] == 1
        assert count["b"] == 1

    def test_hook_error_doesnt_crash(self, manager):
        def bad_hook(path):
            raise ValueError("oops")

        manager.register(
            PluginInfo(
                name="bad",
                version="1.0",
                description="bad",
                hooks={"on_scan_start": bad_hook},
            )
        )

        # Should not raise
        manager.fire_on_scan_start(Path("/test"))

    def test_fire_unknown_hook(self, manager):
        results = manager.fire("nonexistent_hook")
        assert results == []

    def test_unregister_removes_hooks(self, manager):
        called = []

        def hook(path):
            called.append(True)

        manager.register(
            PluginInfo(
                name="test",
                version="1.0",
                description="test",
                hooks={"on_scan_start": hook},
            )
        )
        manager.unregister("test")
        manager.fire_on_scan_start(Path("/test"))
        assert len(called) == 0


class TestLoadPlugin:
    def test_load_from_file(self, manager, tmp_path):
        plugin_file = tmp_path / "my_plugin.py"
        plugin_file.write_text(
            "def register(manager):\n"
            "    from dupeclean.plugins import PluginInfo\n"
            "    manager.register(PluginInfo(\n"
            '        name="loaded",\n'
            '        version="1.0",\n'
            '        description="loaded plugin",\n'
            "    ))\n"
        )
        result = manager.load_plugin(plugin_file)
        assert result is True
        assert "loaded" in manager.plugins

    def test_load_nonexistent(self, manager, tmp_path):
        result = manager.load_plugin(tmp_path / "nope.py")
        assert result is False

    def test_load_no_register(self, manager, tmp_path):
        plugin_file = tmp_path / "no_register.py"
        plugin_file.write_text("x = 1\n")
        result = manager.load_plugin(plugin_file)
        assert result is False


class TestLoadPluginsFromDir:
    def test_load_directory(self, manager, tmp_path):
        (tmp_path / "plugin1.py").write_text(
            "def register(manager):\n"
            "    from dupeclean.plugins import PluginInfo\n"
            "    manager.register(PluginInfo(\n"
            '        name="p1", version="1.0", description="p1"\n'
            "    ))\n"
        )
        (tmp_path / "plugin2.py").write_text(
            "def register(manager):\n"
            "    from dupeclean.plugins import PluginInfo\n"
            "    manager.register(PluginInfo(\n"
            '        name="p2", version="1.0", description="p2"\n'
            "    ))\n"
        )
        (tmp_path / "_private.py").write_text("def register(manager): pass\n")

        loaded = manager.load_plugins_from_dir(tmp_path)
        assert loaded == 2
        assert "p1" in manager.plugins
        assert "p2" in manager.plugins

    def test_empty_directory(self, manager, tmp_path):
        loaded = manager.load_plugins_from_dir(tmp_path)
        assert loaded == 0

    def test_nonexistent_directory(self, manager, tmp_path):
        loaded = manager.load_plugins_from_dir(tmp_path / "nope")
        assert loaded == 0


class TestBuiltinPlugins:
    def test_create_builtin(self):
        plugins = create_builtin_plugins()
        assert len(plugins) >= 1
        assert plugins[0].name == "summary"
