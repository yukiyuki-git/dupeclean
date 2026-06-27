"""Tests for DupeClean hasher."""
from pathlib import Path
import pytest
from dupeclean.config import HasherConfig
from dupeclean.hasher import Hasher
from dupeclean.models import FileInfo, HashStage


@pytest.fixture
def sample_files(tmp_path):
    files = []
    for name, content in [("a.txt", b"hello world"), ("b.txt", b"hello world"), ("c.txt", b"different"), ("d.txt", b"hello world again longer")]:
        path = tmp_path / name
        path.write_bytes(content)
        fi = FileInfo.from_path(path)
        if fi:
            files.append(fi)
    return files


class TestHasher:
    def test_quick_hash(self, sample_files):
        hasher = Hasher()
        hashed = hasher.hash_files(sample_files, HashStage.QUICK, threads=1)
        for fi in hashed:
            assert fi.quick_hash is not None

    def test_medium_hash(self, sample_files):
        hasher = Hasher()
        hashed = hasher.hash_files(sample_files, HashStage.MEDIUM, threads=1)
        for fi in hashed:
            assert fi.medium_hash is not None

    def test_full_hash(self, sample_files):
        hasher = Hasher()
        hashed = hasher.hash_files(sample_files, HashStage.FULL, threads=1)
        for fi in hashed:
            assert fi.full_hash is not None

    def test_same_content_same_hash(self, sample_files):
        hasher = Hasher()
        hashed = hasher.hash_files(sample_files, HashStage.QUICK, threads=1)
        a_hash = next(f.quick_hash for f in hashed if f.path.name == "a.txt")
        b_hash = next(f.quick_hash for f in hashed if f.path.name == "b.txt")
        assert a_hash == b_hash

    def test_different_content_different_hash(self, sample_files):
        hasher = Hasher()
        hashed = hasher.hash_files(sample_files, HashStage.QUICK, threads=1)
        a_hash = next(f.quick_hash for f in hashed if f.path.name == "a.txt")
        c_hash = next(f.quick_hash for f in hashed if f.path.name == "c.txt")
        assert a_hash != c_hash

    def test_config_algorithms(self, sample_files):
        for algo in ("xxhash", "md5", "sha256"):
            config = HasherConfig(algorithm=algo)
            hasher = Hasher(config)
            hashed = hasher.hash_files(sample_files[:1], HashStage.FULL, threads=1)
            assert hashed[0].full_hash is not None
