"""File deduplication pipeline module for DupeClean.

Chain dedup operations into composable pipelines.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineStage:
    """A stage in a dedup pipeline."""

    name: str
    transform: Callable[[Any], Any]
    description: str = ""


@dataclass
class Pipeline:
    """A composable dedup pipeline."""

    name: str
    stages: list[PipelineStage] = field(default_factory=list)

    def add_stage(
        self,
        name: str,
        transform: Callable[[Any], Any],
        description: str = "",
    ) -> Pipeline:
        """Add a stage to the pipeline. Returns self for chaining."""
        self.stages.append(
            PipelineStage(
                name=name,
                transform=transform,
                description=description,
            )
        )
        return self

    def execute(self, data: Any) -> Any:
        """Execute the pipeline on data."""
        result = data
        for stage in self.stages:
            result = stage.transform(result)
        return result

    @property
    def stage_count(self) -> int:
        return len(self.stages)


def create_scan_pipeline() -> Pipeline:
    """Create a standard scan pipeline."""
    return Pipeline(name="Scan Pipeline")


def create_filter_pipeline() -> Pipeline:
    """Create a file filter pipeline."""
    return Pipeline(name="Filter Pipeline")


def create_hash_pipeline() -> Pipeline:
    """Create a hashing pipeline."""
    return Pipeline(name="Hash Pipeline")


def compose_pipelines(*pipelines: Pipeline) -> Pipeline:
    """Compose multiple pipelines into one."""
    composed = Pipeline(name="Composed Pipeline")
    for pipeline in pipelines:
        for stage in pipeline.stages:
            composed.stages.append(stage)
    return composed


def format_pipeline(pipeline: Pipeline) -> str:
    """Format pipeline as text."""
    if not pipeline.stages:
        return f"Pipeline '{pipeline.name}': (empty)"

    lines = [
        f"Pipeline: {pipeline.name} ({pipeline.stage_count} stages)",
        "",
    ]

    for i, stage in enumerate(pipeline.stages):
        desc = stage.description or stage.name
        lines.append(f"  {i + 1}. {stage.name}: {desc}")

    return "\n".join(lines)
