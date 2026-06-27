"""Tests for DupeClean file explorer module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dupeclean.explorer import (
    ExplorerNode,
    FileExplorer,
)


@pytest.fixture
def explorer(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    (tmp_path / "file2.py").write_text("print('hi')")
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "nested.txt").write_text("world")
    return FileExplorer(tmp_path)


class TestFileExplorer:
    def test_get_children(self, explorer):
        children = explorer.get_children()
        assert len(children) == 3  # file1, file2, subdir

    def test_navigate(self, explorer, tmp_path):
        sub = tmp_path / "subdir"
        explorer.navigate(sub)
        assert explorer.current == sub

    def test_go_up(self, explorer, tmp_path):
        sub = tmp_path / "subdir"
        explorer.navigate(sub)
        explorer.go_up()
        assert explorer.current == tmp_path

    def test_render(self, explorer):
        text = explorer.render()
        assert "file1.txt" in text
        assert "file2.py" in text


class TestExplorerNode:
    def test_dir_icon(self):
        node = ExplorerNode(name="test", path=Path("/test"), is_dir=True)
        assert node.icon == "📁"

    def test_file_icon(self):
        node = ExplorerNode(name="test", path=Path("/test"), is_dir=False)
        assert node.icon == "📄"

    def test_size_display(self):
        node = ExplorerNode(name="test", path=Path("/test"), is_dir=False, size=1024)
        assert "B" in node.size_display
