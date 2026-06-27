"""Tests for DupeClean file annotation module."""

from __future__ import annotations

import pytest

from dupeclean.annotations import (
    AnnotationStore,
    format_annotations,
)


@pytest.fixture
def store(tmp_path):
    return AnnotationStore(root=tmp_path)


class TestAnnotationStore:
    def test_get_creates_entry(self, store, tmp_path):
        f = tmp_path / "file.txt"
        ann = store.get(f)
        assert ann.path == "file.txt"

    def test_set_note(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.set_note(f, "Important file")
        assert store.get(f).note == "Important file"

    def test_set_rating(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.set_rating(f, 4)
        assert store.get(f).rating == 4

    def test_rating_clamped(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.set_rating(f, 10)
        assert store.get(f).rating == 5
        store.set_rating(f, -1)
        assert store.get(f).rating == 0

    def test_add_label(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.add_label(f, "important")
        store.add_label(f, "review")
        assert "important" in store.get(f).labels
        assert "review" in store.get(f).labels

    def test_add_duplicate_label(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.add_label(f, "important")
        store.add_label(f, "important")
        assert store.get(f).labels.count("important") == 1

    def test_set_custom(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.set_custom(f, "author", "Alice")
        assert store.get(f).custom["author"] == "Alice"

    def test_find_by_label(self, store, tmp_path):
        store.add_label(tmp_path / "a.txt", "important")
        store.add_label(tmp_path / "b.txt", "important")
        store.add_label(tmp_path / "c.txt", "other")
        results = store.find_by_label("important")
        assert len(results) == 2

    def test_find_by_rating(self, store, tmp_path):
        store.set_rating(tmp_path / "a.txt", 5)
        store.set_rating(tmp_path / "b.txt", 3)
        store.set_rating(tmp_path / "c.txt", 1)
        results = store.find_by_rating(min_rating=3)
        assert len(results) == 2

    def test_save_and_load(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.set_note(f, "test note")
        store.set_rating(f, 4)
        store.add_label(f, "important")
        store.save()

        loaded = AnnotationStore.load(tmp_path)
        ann = loaded.get(f)
        assert ann.note == "test note"
        assert ann.rating == 4
        assert "important" in ann.labels

    def test_load_nonexistent(self, tmp_path):
        store = AnnotationStore.load(tmp_path)
        assert len(store.annotations) == 0


class TestFormatAnnotations:
    def test_empty(self, store):
        assert "No annotations" in format_annotations(store)

    def test_with_annotations(self, store, tmp_path):
        f = tmp_path / "file.txt"
        store.set_note(f, "Important")
        store.set_rating(f, 4)
        text = format_annotations(store)
        assert "Important" in text
