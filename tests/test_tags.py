"""Tests for DupeClean file tagging module."""

from __future__ import annotations

import pytest

from dupeclean.tags import TagStore, format_tag_summary


@pytest.fixture
def store(tmp_path):
    return TagStore(root=tmp_path)


class TestTagStore:
    def test_add_tag(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.add_tag(f, "important")
        assert "important" in store.get_tags(f)

    def test_add_duplicate_tag(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.add_tag(f, "important")
        store.add_tag(f, "important")
        assert store.get_tags(f).count("important") == 1

    def test_remove_tag(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.add_tag(f, "important")
        assert store.remove_tag(f, "important") is True
        assert "important" not in store.get_tags(f)

    def test_remove_nonexistent(self, store, tmp_path):
        f = tmp_path / "file.txt"
        assert store.remove_tag(f, "nope") is False

    def test_set_note(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.set_note(f, "This is a note")
        rel = str(f.relative_to(tmp_path))
        assert store.tags[rel].note == "This is a note"

    def test_find_by_tag(self, store, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        store.add_tag(f1, "important")
        store.add_tag(f2, "important")
        store.add_tag(tmp_path / "c.txt", "other")

        results = store.find_by_tag("important")
        assert len(results) == 2

    def test_all_tags(self, store, tmp_path):
        store.add_tag(tmp_path / "a.txt", "important")
        store.add_tag(tmp_path / "b.txt", "archive")
        store.add_tag(tmp_path / "c.txt", "important")

        tags = store.all_tags()
        assert "important" in tags
        assert "archive" in tags

    def test_save_and_load(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.add_tag(f, "important")
        store.set_note(f, "test note")
        store.save()

        loaded = TagStore.load(tmp_path)
        assert "important" in loaded.get_tags(f)

    def test_load_nonexistent(self, tmp_path):
        store = TagStore.load(tmp_path)
        assert len(store.tags) == 0

    def test_empty_store(self, store):
        assert store.all_tags() == []
        assert store.find_by_tag("nope") == []


class TestFormatTagSummary:
    def test_empty(self, store):
        assert "No tags" in format_tag_summary(store)

    def test_with_tags(self, store, tmp_path):
        store.add_tag(tmp_path / "a.txt", "important")
        store.add_tag(tmp_path / "b.txt", "archive")
        text = format_tag_summary(store)
        assert "important" in text
        assert "archive" in text
