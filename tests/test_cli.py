"""Tests for DupeClean CLI."""

from dupeclean.cli import build_parser, main


class TestBuildParser:
    def test_default_args(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.path == "."
        assert args.cli is False

    def test_path_arg(self):
        parser = build_parser()
        args = parser.parse_args(["/some/path"])
        assert args.path == "/some/path"

    def test_cli_mode(self):
        parser = build_parser()
        args = parser.parse_args(["--cli"])
        assert args.cli is True

    def test_duplicates_mode(self):
        parser = build_parser()
        args = parser.parse_args(["--duplicates", "/path"])
        assert args.duplicates is True

    def test_top_n(self):
        parser = build_parser()
        args = parser.parse_args(["--top", "20"])
        assert args.top == 20

    def test_report_format(self):
        parser = build_parser()
        args = parser.parse_args(["--report", "html"])
        assert args.report == "html"


class TestMainCLI:
    def test_cli_summary(self, tmp_path):
        (tmp_path / "test.txt").write_text("hello")
        (tmp_path / "test2.txt").write_text("world")
        result = main(["--cli", str(tmp_path)])
        assert result == 0

    def test_cli_top(self, tmp_path):
        (tmp_path / "big.bin").write_bytes(b"\0" * 1024)
        (tmp_path / "small.txt").write_text("hi")
        result = main(["--cli", "--top", "5", str(tmp_path)])
        assert result == 0

    def test_cli_duplicates(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"same")
        (tmp_path / "b.txt").write_bytes(b"same")
        result = main(["--cli", "--duplicates", str(tmp_path)])
        assert result == 0

    def test_nonexistent_path(self):
        result = main(["--cli", "/nonexistent/path/that/does/not/exist"])
        assert result == 1

    def test_report_json(self, tmp_path):
        (tmp_path / "test.txt").write_text("hello")
        result = main(["--report", "json", str(tmp_path)])
        assert result == 0
