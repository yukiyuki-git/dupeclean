"""Tests for DupeClean group workflow module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.group_workflow import (
    GroupWorkflow,
    WorkflowStage,
    create_group_workflow,
)
from dupeclean.models import DuplicateGroup, FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestGroupWorkflow:
    def test_add_stage(self):
        wf = GroupWorkflow(name="test")
        wf.add_stage("step1", "First step")
        assert len(wf.stages) == 1

    def test_progress_empty(self):
        wf = GroupWorkflow(name="test")
        assert wf.progress == 0.0

    def test_progress_partial(self):
        wf = GroupWorkflow(name="test")
        wf.add_stage("a", "do a")
        wf.add_stage("b", "do b")
        wf.stages[0].status = "completed"
        assert wf.progress == 0.5

    def test_is_complete(self):
        wf = GroupWorkflow(name="test")
        wf.add_stage("a", "do a")
        wf.stages[0].status = "completed"
        assert wf.is_complete is True

    def test_current(self):
        wf = GroupWorkflow(name="test")
        wf.add_stage("a", "do a")
        assert wf.current is not None
        assert wf.current.name == "a"

    def test_advance(self):
        wf = GroupWorkflow(name="test")
        wf.add_stage("a", "do a")
        wf.add_stage("b", "do b")
        wf.advance()
        assert wf.current_stage == 1

    def test_complete_current(self):
        wf = GroupWorkflow(name="test")
        wf.add_stage("a", "do a")
        wf.add_stage("b", "do b")
        wf.complete_current()
        assert wf.stages[0].status == "completed"
        assert wf.current_stage == 1

    def test_render(self):
        wf = GroupWorkflow(name="test")
        wf.add_stage("scan", "Scan files")
        text = wf.render()
        assert "test" in text
        assert "scan" in text


class TestCreateGroupWorkflow:
    def test_has_stages(self):
        groups = [
            DuplicateGroup(
                group_id=0,
                hash_value="abc",
                file_size=100,
                files=[_fi("/a"), _fi("/b")],
            )
        ]
        wf = create_group_workflow(groups)
        assert len(wf.stages) == 8
        assert wf.name == "Group Processing"
        assert wf.groups == groups


class TestWorkflowStage:
    def test_defaults(self):
        stage = WorkflowStage(name="test", description="test desc")
        assert stage.status == "pending"
