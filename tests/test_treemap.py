"""Tests for DupeClean enhanced treemap module."""

from __future__ import annotations

from pathlib import Path

import pytest

from dupeclean.models import DirInfo
from dupeclean.treemap import (
    TreemapNode,
    build_treemap,
    format_treemap,
    treemap_to_dict,
)


@pytest.fixture
def sample_dirs():
    dirs = {
        Path("/root"): DirInfo(
            path=Path("/root"),
            total_size=10000,
            file_count=10,
            children=[
                DirInfo(
                    path=Path("/root/a"),
                    total_size=5000,
                    file_count=5,
                ),
                DirInfo(
                    path=Path("/root/b"),
                    total_size=3000,
                    file_count=3,
                ),
                DirInfo(
                    path=Path("/root/c"),
                    total_size=2000,
                    file_count=2,
                ),
            ],
        ),
        Path("/root/a"): DirInfo(
            path=Path("/root/a"), total_size=5000, file_count=5
        ),
        Path("/root/b"): DirInfo(
            path=Path("/root/b"), total_size=3000, file_count=3
        ),
        Path("/root/c"): DirInfo(
            path=Path("/root/c"), total_size=2000, file_count=2
        ),
    }
    return dirs


class TestBuildTreemap:
    def test_basic_treemap(self, sample_dirs):
        node = build_treemap(sample_dirs, Path("/root"))
        assert node.size == 10000
        assert node.percentage == 100.0
        assert node.children is not None
        assert len(node.children) == 3

    def test_sorted_by_size(self, sample_dirs):
        node = build_treemap(sample_dirs, Path("/root"))
        sizes = [c.size for c in node.children]
        assert sizes == sorted(sizes, reverse=True)

    def test_max_children(self, sample_dirs):
        node = build_treemap(
            sample_dirs, Path("/root"), max_children=2
        )
        # 2 real children + 1 "(other)" node
        assert len(node.children) == 3

    def test_empty_root(self):
        node = build_treemap({}, Path("/empty"))
        assert node.size == 0

    def test_max_depth(self, sample_dirs):
        node = build_treemap(
            sample_dirs, Path("/root"), max_depth=1
        )
        for child in node.children:
            assert child.children is None or len(child.children) == 0


class TestFormatTreemap:
    def test_contains_total(self, sample_dirs):
        node = build_treemap(sample_dirs, Path("/root"))
        text = format_treemap(node)
        assert "10" in text  # 10000 -> contains 10

    def test_contains_bars(self, sample_dirs):
        node = build_treemap(sample_dirs, Path("/root"))
        text = format_treemap(node, show_bar=True)
        assert "█" in text

    def test_no_bars(self, sample_dirs):
        node = build_treemap(sample_dirs, Path("/root"))
        text = format_treemap(node, show_bar=False)
        assert "█" not in text

    def test_contains_children(self, sample_dirs):
        node = build_treemap(sample_dirs, Path("/root"))
        text = format_treemap(node)
        assert "a" in text
        assert "b" in text


class TestTreemapToDict:
    def test_basic_dict(self, sample_dirs):
        node = build_treemap(sample_dirs, Path("/root"))
        result = treemap_to_dict(node)
        assert result["name"] == "root"
        assert result["size"] == 10000
        assert "children" in result
        assert len(result["children"]) == 3

    def test_leaf_node(self):
        node = TreemapNode(
            name="file.txt",
            path=Path("/test/file.txt"),
            size=100,
            depth=1,
            percentage=50.0,
            is_dir=False,
        )
        result = treemap_to_dict(node)
        assert "children" not in result
