"""Tests for DupeClean file scoring module."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.scoring import (
    ScoreComponent,
    compute_file_score,
    format_file_scores,
    score_by_age,
    score_by_duplicates,
    score_by_extension,
    score_by_path_depth,
    score_by_size,
    score_files,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestScoreComponent:
    def test_weighted(self):
        c = ScoreComponent(name="test", weight=0.5, value=0.8)
        assert c.weighted == 0.4


class TestScoreBySize:
    def test_large_file(self):
        score = score_by_size(_fi("/a", 1000000), 1000000)
        assert score.value == 1.0

    def test_small_file(self):
        score = score_by_size(_fi("/a", 500), 1000)
        assert score.value == 0.5


class TestScoreByAge:
    def test_old_file(self):
        old_time = time.time() - (400 * 86400)
        score = score_by_age(_fi("/a", mtime=old_time), 365)
        assert score.value >= 1.0  # Clamped to 1.0

    def test_new_file(self):
        score = score_by_age(_fi("/a", mtime=time.time()), 365)
        assert score.value < 0.1


class TestScoreByExtension:
    def test_priority_ext(self):
        score = score_by_extension(_fi("/a.tmp"))
        assert score.value == 1.0

    def test_normal_ext(self):
        score = score_by_extension(_fi("/a.py"))
        assert score.value == 0.0


class TestScoreByPathDepth:
    def test_deep(self):
        score = score_by_path_depth(_fi("/a/b/c/d/e.txt"))
        assert score.value > 0.3

    def test_shallow(self):
        score = score_by_path_depth(_fi("/a.txt"))
        assert score.value < 0.3


class TestScoreByDuplicates:
    def test_duplicate(self):
        score = score_by_duplicates(_fi("/a"), True)
        assert score.value == 1.0

    def test_unique(self):
        score = score_by_duplicates(_fi("/a"), False)
        assert score.value == 0.0


class TestComputeFileScore:
    def test_basic(self):
        fi = _fi("/test/big.tmp", 1000000, time.time() - 100 * 86400)
        score = compute_file_score(fi)
        assert score.total > 0
        assert len(score.components) == 5

    def test_max_possible(self):
        fi = _fi("/a")
        score = compute_file_score(fi)
        assert score.max_possible == 1.0  # Sum of weights


class TestScoreFiles:
    def test_sorted(self):
        files = [
            _fi("/small.txt", 100),
            _fi("/big.tmp", 1000000),
        ]
        scores = score_files(files)
        assert scores[0].file.path.name == "big.tmp"

    def test_with_duplicates(self):
        files = [_fi("/a.txt", 100), _fi("/b.txt", 100)]
        dup_set = {Path("/b.txt")}
        scores = score_files(files, duplicate_set=dup_set)
        # Duplicate should score higher
        b_score = next(s for s in scores if s.file.path.name == "b.txt")
        a_score = next(s for s in scores if s.file.path.name == "a.txt")
        assert b_score.total >= a_score.total


class TestFormatFileScores:
    def test_empty(self):
        assert "No files" in format_file_scores([])

    def test_with_scores(self):
        files = [_fi("/a.py", 1000), _fi("/b.tmp", 500)]
        scores = score_files(files)
        text = format_file_scores(scores)
        assert "File Scores" in text
