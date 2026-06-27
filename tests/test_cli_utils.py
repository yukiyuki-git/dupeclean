"""Tests for DupeClean CLI integration module."""

from __future__ import annotations

from dupeclean.cli_utils import (
    CLIResult,
    build_config_from_args,
    format_error,
    format_size_for_cli,
    format_success,
    validate_path,
    validate_threads,
)


class TestValidatePath:
    def test_valid_path(self, tmp_path):
        valid, path, _err = validate_path(str(tmp_path))
        assert valid is True
        assert path.exists()

    def test_nonexistent_path(self):
        valid, _path, err = validate_path("/nonexistent/path")
        assert valid is False
        assert "not found" in err.lower()


class TestValidateThreads:
    def test_valid(self):
        valid, _err = validate_threads(4)
        assert valid is True

    def test_zero_threads(self):
        valid, _err = validate_threads(0)
        assert valid is False

    def test_too_many_threads(self):
        valid, _err = validate_threads(100)
        assert valid is False


class TestFormatSizeForCli:
    def test_basic(self):
        assert "B" in format_size_for_cli(1024)


class TestBuildConfigFromArgs:
    def test_threads(self):
        config = build_config_from_args({"threads": 8})
        assert config.scanner.threads == 8

    def test_follow_symlinks(self):
        config = build_config_from_args({"follow_symlinks": True})
        assert config.scanner.follow_symlinks is True

    def test_empty_args(self):
        config = build_config_from_args({})
        assert config.scanner.threads == 4  # Default


class TestFormatError:
    def test_basic(self):
        text = format_error("Something failed")
        assert "Error:" in text
        assert "Something failed" in text

    def test_with_details(self):
        text = format_error("Failed", "Permission denied")
        assert "Permission denied" in text


class TestFormatSuccess:
    def test_basic(self):
        text = format_success("Done")
        assert "Success:" in text


class TestCLIResult:
    def test_defaults(self):
        result = CLIResult(success=True, message="ok")
        assert result.exit_code == 0
