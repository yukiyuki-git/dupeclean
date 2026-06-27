"""File deduplication cleanup pipeline for DupeClean.

Chain cleanup operations into composable pipelines.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineStage:
    """A stage in a cleanup pipeline."""

    name: str
    transform: Callable[[Any], Any]
    description: str = ""


@dataclass
class CleanupPipeline:
    """A composable cleanup pipeline."""

    name: str
    stages: list[PipelineStage] = field(default_factory=list)

    def add_stage(
        self,
        name: str,
        transform: Callable[[Any], Any],
        description: str = "",
    ) -> CleanupPipeline:
        self.stages.append(PipelineStage(name=name, transform=transform, description=description))
        return self

    def execute(self, data: Any) -> Any:
        """Execute pipeline on data."""
        result = data
        for stage in self.stages:
            result = stage.transform(result)
        return result

    @property
    def stage_count(self) -> int:
        return len(self.stages)

    def render(self) -> str:
        """Render pipeline as text."""
        if not self.stages:
            return f"Pipeline '{self.name}': (empty)"
        lines = [f"Pipeline: {self.name} ({self.stage_count} stages)", ""]
        for i, stage in enumerate(self.stages):
            desc = stage.description or stage.name
            lines.append(f"  {i + 1}. {stage.name}: {desc}")
        return "\n".join(lines)


def create_scan_pipeline() -> CleanupPipeline:
    """Create a scan pipeline."""
    return CleanupPipeline(name="Scan Pipeline")


def create_full_pipeline() -> CleanupPipeline:
    """Create a full cleanup pipeline."""
    return CleanupPipeline(name="Full Pipeline")
