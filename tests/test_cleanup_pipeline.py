"""Tests for DupeClean cleanup pipeline module."""

from __future__ import annotations

from dupeclean.cleanup_pipeline import (
    CleanupPipeline,
    PipelineStage,
    create_full_pipeline,
    create_scan_pipeline,
)


class TestCleanupPipeline:
    def test_add_stage(self):
        p = CleanupPipeline(name="test")
        p.add_stage("step1", lambda x: x, "first step")
        assert p.stage_count == 1

    def test_execute_single(self):
        p = CleanupPipeline(name="test")
        p.add_stage("double", lambda x: x * 2)
        assert p.execute(5) == 10

    def test_execute_chain(self):
        p = CleanupPipeline(name="test")
        p.add_stage("double", lambda x: x * 2)
        p.add_stage("add_one", lambda x: x + 1)
        assert p.execute(5) == 11

    def test_chaining(self):
        p = CleanupPipeline(name="test")
        result = p.add_stage("a", lambda x: x + 1).add_stage("b", lambda x: x * 2)
        assert result is p
        assert p.stage_count == 2

    def test_render_empty(self):
        p = CleanupPipeline(name="test")
        assert "empty" in p.render()

    def test_render_with_stages(self):
        p = CleanupPipeline(name="test")
        p.add_stage("scan", lambda x: x, "Scan files")
        text = p.render()
        assert "scan" in text


class TestCreatePipelines:
    def test_scan(self):
        p = create_scan_pipeline()
        assert p.name == "Scan Pipeline"

    def test_full(self):
        p = create_full_pipeline()
        assert p.name == "Full Pipeline"


class TestPipelineStage:
    def test_defaults(self):
        stage = PipelineStage(name="test", transform=lambda x: x)
        assert stage.description == ""
