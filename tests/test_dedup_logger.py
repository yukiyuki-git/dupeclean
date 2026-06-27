"""Tests for DupeClean logging module."""

from __future__ import annotations

from dupeclean.dedup_logger import (
    DedupLogger,
    LogEntry,
    format_log_entries,
)


class TestDedupLogger:
    def test_info(self):
        logger = DedupLogger()
        logger.info("Test message")
        assert len(logger.entries) == 1
        assert logger.entries[0].level == "info"

    def test_debug_below_min_level(self):
        logger = DedupLogger(min_level="info")
        logger.debug("Debug message")
        assert len(logger.entries) == 0

    def test_warning(self):
        logger = DedupLogger()
        logger.warning("Warning message")
        assert len(logger.entries) == 1

    def test_error(self):
        logger = DedupLogger()
        logger.error("Error message")
        assert len(logger.entries) == 1

    def test_get_by_level(self):
        logger = DedupLogger()
        logger.info("info 1")
        logger.error("error 1")
        logger.info("info 2")
        assert len(logger.get_by_level("info")) == 2
        assert len(logger.get_by_level("error")) == 1

    def test_get_recent(self):
        logger = DedupLogger()
        for i in range(100):
            logger.info(f"Message {i}")
        recent = logger.get_recent(10)
        assert len(recent) == 10
        assert recent[0].message == "Message 90"

    def test_max_entries(self):
        logger = DedupLogger(max_entries=10)
        for i in range(20):
            logger.info(f"Message {i}")
        assert len(logger.entries) <= 10

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "log.json"
        logger = DedupLogger()
        logger.info("Test message", module="test")
        logger.save(path)
        assert path.exists()

        loaded = DedupLogger.load(path)
        assert len(loaded.entries) == 1
        assert loaded.entries[0].message == "Test message"

    def test_load_nonexistent(self, tmp_path):
        logger = DedupLogger.load(tmp_path / "nope")
        assert len(logger.entries) == 0


class TestLogEntry:
    def test_defaults(self):
        entry = LogEntry(timestamp=0, level="info", message="test")
        assert entry.module == ""


class TestFormatLogEntries:
    def test_empty(self):
        assert "No log" in format_log_entries([])

    def test_with_entries(self):
        entries = [
            LogEntry(timestamp=1000000, level="info", message="Test"),
        ]
        text = format_log_entries(entries)
        assert "[I]" in text
        assert "Test" in text
