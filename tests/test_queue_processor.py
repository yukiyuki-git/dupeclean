"""Tests for DupeClean queue processor module."""

from __future__ import annotations

from dupeclean.queue_processor import (
    ProcessorConfig,
    ProcessorResult,
    QueueProcessor,
    format_processor_result,
)


class TestQueueProcessor:
    def test_process_batch(self):
        processor = QueueProcessor()
        result = processor.process_batch([1, 2, 3], lambda x: True)
        assert result.processed == 3
        assert result.succeeded == 3

    def test_process_batch_with_failures(self):
        processor = QueueProcessor()
        result = processor.process_batch([1, 2, 3], lambda x: x != 2)
        assert result.succeeded == 2
        assert result.failed == 1

    def test_batch_size_limit(self):
        config = ProcessorConfig(batch_size=2)
        processor = QueueProcessor(config)
        result = processor.process_batch([1, 2, 3, 4, 5], lambda x: True)
        assert result.processed == 2

    def test_total_processed(self):
        processor = QueueProcessor()
        processor.process_batch([1, 2], lambda x: True)
        processor.process_batch([3, 4], lambda x: True)
        assert processor.total_processed == 4


class TestProcessorResult:
    def test_success_rate(self):
        result = ProcessorResult(processed=10, succeeded=8)
        assert result.success_rate == 0.8

    def test_zero_processed(self):
        result = ProcessorResult()
        assert result.success_rate == 0.0


class TestProcessorConfig:
    def test_defaults(self):
        config = ProcessorConfig()
        assert config.max_workers == 1
        assert config.batch_size == 10


class TestFormatProcessorResult:
    def test_basic(self):
        result = ProcessorResult(processed=10, succeeded=8, failed=2, duration=1.5)
        text = format_processor_result(result)
        assert "10" in text
        assert "1.50s" in text
