"""Tests for DupeClean storage manager."""

from __future__ import annotations

from dupeclean.storage import (
    StorageEntry,
    StorageManager,
    format_storage_stats,
)


class TestStorageManager:
    def test_add_reference(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100, "/a.txt")
        assert mgr.total_entries == 1
        assert mgr.total_references == 1

    def test_add_duplicate_reference(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100, "/a.txt")
        mgr.add_reference("abc", 100, "/b.txt")
        assert mgr.total_entries == 1
        assert mgr.total_references == 2

    def test_remove_reference(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100, "/a.txt")
        mgr.add_reference("abc", 100, "/b.txt")
        removed = mgr.remove_reference("abc")
        assert removed is False  # Still has 1 ref
        assert mgr.total_references == 1

    def test_remove_last_reference(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100, "/a.txt")
        removed = mgr.remove_reference("abc")
        assert removed is True
        assert mgr.total_entries == 0

    def test_remove_nonexistent(self):
        mgr = StorageManager()
        assert mgr.remove_reference("nope") is False

    def test_get_entry(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100, "/a.txt")
        entry = mgr.get_entry("abc")
        assert entry is not None
        assert entry.size == 100

    def test_get_entry_nonexistent(self):
        mgr = StorageManager()
        assert mgr.get_entry("nope") is None

    def test_get_duplicated(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100)
        mgr.add_reference("abc", 100)
        mgr.add_reference("def", 200)
        dupes = mgr.get_duplicated()
        assert len(dupes) == 1
        assert dupes[0].content_hash == "abc"

    def test_wasted_size(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 1000)
        mgr.add_reference("abc", 1000)
        assert mgr.wasted_size == 1000

    def test_stats(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100)
        mgr.add_reference("abc", 100)
        mgr.add_reference("def", 200)
        stats = mgr.stats()
        assert stats["total_entries"] == 2
        assert stats["total_references"] == 3
        assert stats["wasted_size"] == 100


class TestStorageEntry:
    def test_size_display(self):
        entry = StorageEntry(content_hash="abc", size=1024)
        assert "B" in entry.size_display


class TestFormatStorageStats:
    def test_basic(self):
        mgr = StorageManager()
        mgr.add_reference("abc", 100)
        mgr.add_reference("abc", 100)
        text = format_storage_stats(mgr)
        assert "Storage" in text
        assert "2" in text
