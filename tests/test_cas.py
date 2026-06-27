"""Tests for DupeClean content-addressable storage."""

from __future__ import annotations

from dupeclean.cas import (
    CAS,
    ContentRef,
    format_cas_stats,
)


class TestCAS:
    def test_store(self):
        cas = CAS()
        h = cas.store(b"hello world")
        assert len(h) == 64  # sha256
        assert cas.exists(h)

    def test_dedup_same_content(self):
        cas = CAS()
        h1 = cas.store(b"same content")
        h2 = cas.store(b"same content")
        assert h1 == h2
        assert cas.chunk_count == 1
        assert cas.retrieve(h1).ref_count == 2

    def test_different_content(self):
        cas = CAS()
        h1 = cas.store(b"content a")
        h2 = cas.store(b"content b")
        assert h1 != h2
        assert cas.chunk_count == 2

    def test_retrieve(self):
        cas = CAS()
        h = cas.store(b"test data")
        ref = cas.retrieve(h)
        assert ref is not None
        assert ref.size == 9

    def test_retrieve_nonexistent(self):
        cas = CAS()
        assert cas.retrieve("nonexistent") is None

    def test_exists(self):
        cas = CAS()
        h = cas.store(b"data")
        assert cas.exists(h) is True
        assert cas.exists("nope") is False

    def test_add_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        cas = CAS()
        h = cas.add_file(f)
        assert h is not None
        assert cas.exists(h)

    def test_add_file_nonexistent(self, tmp_path):
        cas = CAS()
        assert cas.add_file(tmp_path / "nope") is None

    def test_add_file_chunks(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(b"x" * 10000)
        cas = CAS()
        hashes = cas.add_file_chunks(f, chunk_size=1024)
        assert len(hashes) > 1
        assert all(cas.exists(h) for h in hashes)


class TestCASStats:
    def test_dedup_ratio(self):
        cas = CAS()
        cas.store(b"same")
        cas.store(b"same")
        cas.store(b"same")
        stats = cas.stats()
        assert stats.dedup_ratio > 0.5
        assert stats.unique_chunks == 1
        assert stats.total_chunks == 3

    def test_storage_saved(self):
        cas = CAS()
        cas.store(b"x" * 1000)
        cas.store(b"x" * 1000)
        stats = cas.stats()
        assert stats.storage_saved == 1000

    def test_no_dedup(self):
        cas = CAS()
        cas.store(b"a")
        cas.store(b"b")
        stats = cas.stats()
        assert stats.dedup_ratio == 0.0


class TestContentRef:
    def test_defaults(self):
        ref = ContentRef(hash="abc", size=100)
        assert ref.ref_count == 1


class TestCASProperties:
    def test_chunk_count(self):
        cas = CAS()
        cas.store(b"a")
        cas.store(b"b")
        assert cas.chunk_count == 2

    def test_total_size(self):
        cas = CAS()
        cas.store(b"hello")
        cas.store(b"world")
        assert cas.total_size == 10

    def test_total_size_display(self):
        cas = CAS()
        cas.store(b"x" * 2048)
        assert "B" in cas.total_size_display


class TestFormatCASStats:
    def test_basic(self):
        cas = CAS()
        cas.store(b"same")
        cas.store(b"same")
        text = format_cas_stats(cas)
        assert "Content-Addressable" in text
        assert "1" in text
