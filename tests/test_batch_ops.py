"""Tests for DupeClean batch operations module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.batch_ops import (
    BatchOperation,
    BatchResult,
    execute_batch,
    format_batch_result,
)
from dupeclean.models import FileInfo


def _fi(path: str, size: int = 100) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=0)


class TestExecuteBatch:
    def test_all_success(self):
        files = [_fi("/a"), _fi("/b"), _fi("/c")]
        result = execute_batch(files, lambda f: (True, ""))
        assert result.succeeded == 3
        assert result.failed == 0

    def test_all_failure(self):
        files = [_fi("/a"), _fi("/b")]
        result = execute_batch(files, lambda f: (False, "error"))
        assert result.failed == 2
        assert len(result.errors) == 2

    def test_mixed(self):
        files = [_fi("/a"), _fi("/b"), _fi("/c")]
        results_iter = iter([(True, ""), (False, "fail"), (True, "")])
        result = execute_batch(files, lambda f: next(results_iter))
        assert result.succeeded == 2
        assert result.failed == 1

    def test_empty(self):
        result = execute_batch([], lambda f: (True, ""))
        assert result.total == 0

    def test_duration(self):
        files = [_fi("/a")]
        result = execute_batch(files, lambda f: (True, ""))
        assert result.duration >= 0


class TestBatchResult:
    def test_success_rate(self):
        result = BatchResult(operation="test", total=10, succeeded=8)
        assert result.success_rate == 0.8

    def test_zero_total(self):
        result = BatchResult(operation="test")
        assert result.success_rate == 0.0


class TestBatchOperation:
    def test_count(self):
        op = BatchOperation(name="test", files=[_fi("/a"), _fi("/b")])
        assert op.count == 2

    def test_total_size(self):
        op = BatchOperation(name="test", files=[_fi("/a", 100), _fi("/b", 200)])
        assert op.total_size == 300


class TestFormatBatchResult:
    def test_basic(self):
        result = BatchResult(operation="test", total=10, succeeded=8, failed=2)
        text = format_batch_result(result)
        assert "test" in text
        assert "8" in text

    def test_with_errors(self):
        result = BatchResult(
            operation="test",
            total=1,
            failed=1,
            errors=["Permission denied"],
        )
        text = format_batch_result(result)
        assert "Permission denied" in text
