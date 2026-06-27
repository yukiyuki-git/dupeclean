"""Tests for DupeClean entropy analysis module."""

from __future__ import annotations

from pathlib import Path

from dupeclean.entropy import (
    EntropyResult,
    analyze_file_entropy,
    calculate_entropy,
    categorize_by_entropy,
    find_high_entropy_files,
)
from dupeclean.models import FileInfo


class TestCalculateEntropy:
    def test_empty_data(self):
        assert calculate_entropy(b"") == 0.0

    def test_single_byte(self):
        # Single repeated byte has 0 entropy
        assert calculate_entropy(b"\x00" * 100) == 0.0

    def test_two_values(self):
        # Two equally likely values: 1 bit of entropy
        data = b"\x00" * 50 + b"\xff" * 50
        ent = calculate_entropy(data)
        assert abs(ent - 1.0) < 0.01

    def test_random_like_data(self):
        # Data with many different bytes has higher entropy
        data = bytes(range(256))
        ent = calculate_entropy(data)
        assert ent == 8.0  # Maximum entropy

    def test_text_has_moderate_entropy(self):
        data = b"Hello, World! " * 100
        ent = calculate_entropy(data)
        assert 3.0 < ent < 5.0

    def test_repeated_pattern_low_entropy(self):
        data = b"AAAA" * 1000
        ent = calculate_entropy(data)
        assert ent < 1.0


class TestAnalyzeFileEntropy:
    def test_normal_file(self, tmp_path):
        f = tmp_path / "code.py"
        f.write_text("print('hello world')\n" * 100)
        result = analyze_file_entropy(f)

        assert result is not None
        assert 2.0 < result.entropy < 6.0
        assert result.category in ("low", "normal")

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        result = analyze_file_entropy(f)

        assert result is not None
        assert result.entropy == 0.0
        assert result.category == "empty"

    def test_binary_file_high_entropy(self, tmp_path):
        f = tmp_path / "random.bin"
        f.write_bytes(bytes(range(256)) * 32)
        result = analyze_file_entropy(f)

        assert result is not None
        assert result.entropy > 7.0

    def test_nonexistent_file(self, tmp_path):
        result = analyze_file_entropy(tmp_path / "nope")
        assert result is None


class TestEntropyResult:
    def test_is_likely_encrypted(self):
        result = EntropyResult(path=Path("/test"), entropy=7.8, file_size=100, category="encrypted")
        assert result.is_likely_encrypted is True

    def test_is_not_encrypted(self):
        result = EntropyResult(path=Path("/test"), entropy=4.5, file_size=100, category="normal")
        assert result.is_likely_encrypted is False

    def test_is_likely_compressed(self):
        result = EntropyResult(path=Path("/test"), entropy=7.2, file_size=100, category="high")
        assert result.is_likely_compressed is True

    def test_description(self):
        for ent, expected_substring in [
            (0.0, "Empty"),
            (3.0, "Low"),
            (5.0, "Normal"),
            (6.5, "Moderate"),
            (7.2, "compressed"),
            (7.8, "encrypted"),
        ]:
            result = EntropyResult(
                path=Path("/test"),
                entropy=ent,
                file_size=100,
                category="test",
            )
            assert expected_substring.lower() in result.description.lower()


class TestFindHighEntropyFiles:
    def test_finds_high_entropy(self, tmp_path):
        normal = tmp_path / "normal.txt"
        normal.write_text("hello world " * 100)
        encrypted = tmp_path / "encrypted.bin"
        encrypted.write_bytes(bytes(range(256)) * 32)

        files = [
            FileInfo.from_path(normal),
            FileInfo.from_path(encrypted),
        ]
        files = [f for f in files if f is not None]

        results = find_high_entropy_files(files, threshold=7.0)
        assert len(results) >= 1
        assert all(r.entropy >= 7.0 for r in results)


class TestCategorizeByEntropy:
    def test_categorization(self, tmp_path):
        (tmp_path / "text.txt").write_text("hello " * 100)
        (tmp_path / "empty.txt").write_bytes(b"")
        (tmp_path / "data.bin").write_bytes(bytes(range(256)) * 32)

        files = []
        for p in tmp_path.iterdir():
            fi = FileInfo.from_path(p)
            if fi:
                files.append(fi)

        cats = categorize_by_entropy(files)
        assert "empty" in cats
        assert "normal" in cats
        assert len(cats["empty"]) >= 1
