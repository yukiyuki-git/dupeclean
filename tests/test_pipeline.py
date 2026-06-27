"""Tests for DupeClean pipeline module."""

from __future__ import annotations

from dupeclean.pipeline import (
    Pipeline,
    PipelineStage,
    compose_pipelines,
    create_filter_pipeline,
    create_hash_pipeline,
    create_scan_pipeline,
    format_pipeline,
)


class TestPipeline:
    def test_add_stage(self):
        p = Pipeline(name="test")
        p.add_stage("step1", lambda x: x, "first step")
        assert p.stage_count == 1

    def test_execute_single(self):
        p = Pipeline(name="test")
        p.add_stage("double", lambda x: x * 2)
        assert p.execute(5) == 10

    def test_execute_chain(self):
        p = Pipeline(name="test")
        p.add_stage("double", lambda x: x * 2)
        p.add_stage("add_one", lambda x: x + 1)
        assert p.execute(5) == 11

    def test_execute_with_list(self):
        p = Pipeline(name="test")
        p.add_stage("filter", lambda x: [i for i in x if i > 3])
        assert p.execute([1, 2, 3, 4, 5]) == [4, 5]

    def test_chaining(self):
        p = Pipeline(name="test")
        result = (
            p.add_stage("a", lambda x: x + 1)
            .add_stage("b", lambda x: x * 2)
            .add_stage("c", lambda x: x - 3)
        )
        assert result is p
        assert p.stage_count == 3

    def test_empty_execute(self):
        p = Pipeline(name="test")
        assert p.execute(42) == 42


class TestPipelineStage:
    def test_defaults(self):
        stage = PipelineStage(name="test", transform=lambda x: x)
        assert stage.description == ""


class TestCreatePipelines:
    def test_scan(self):
        p = create_scan_pipeline()
        assert p.name == "Scan Pipeline"

    def test_filter(self):
        p = create_filter_pipeline()
        assert p.name == "Filter Pipeline"

    def test_hash(self):
        p = create_hash_pipeline()
        assert p.name == "Hash Pipeline"


class TestComposePipelines:
    def test_basic(self):
        p1 = Pipeline(name="p1")
        p1.add_stage("a", lambda x: x + 1)
        p2 = Pipeline(name="p2")
        p2.add_stage("b", lambda x: x * 2)
        composed = compose_pipelines(p1, p2)
        assert composed.stage_count == 2
        assert composed.execute(5) == 12  # (5+1)*2


class TestFormatPipeline:
    def test_empty(self):
        p = Pipeline(name="test")
        text = format_pipeline(p)
        assert "empty" in text

    def test_with_stages(self):
        p = Pipeline(name="test")
        p.add_stage("scan", lambda x: x, "Scan files")
        p.add_stage("hash", lambda x: x, "Hash files")
        text = format_pipeline(p)
        assert "scan" in text
        assert "hash" in text
