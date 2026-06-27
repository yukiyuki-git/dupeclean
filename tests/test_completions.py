"""Tests for DupeClean shell completions."""

from __future__ import annotations

from dupeclean.completions import get_completion, print_completion


class TestGetCompletion:
    def test_bash(self):
        script = get_completion("bash")
        assert script is not None
        assert "dupeclean" in script
        assert "complete" in script

    def test_zsh(self):
        script = get_completion("zsh")
        assert script is not None
        assert "dupeclean" in script
        assert "_arguments" in script

    def test_fish(self):
        script = get_completion("fish")
        assert script is not None
        assert "dupeclean" in script

    def test_unsupported_shell(self):
        assert get_completion("powershell") is None

    def test_case_insensitive(self):
        assert get_completion("BASH") is not None
        assert get_completion("Zsh") is not None
        assert get_completion("FISH") is not None


class TestPrintCompletion:
    def test_print_bash(self, capsys):
        result = print_completion("bash")
        assert result is True
        captured = capsys.readouterr()
        assert "dupeclean" in captured.out

    def test_print_unsupported(self, capsys):
        result = print_completion("unknown")
        assert result is False

    def test_bash_has_dupeclean_and_dc(self):
        script = get_completion("bash")
        assert "dupeclean" in script
        assert "dc" in script

    def test_zsh_has_report_options(self):
        script = get_completion("zsh")
        assert "json" in script
        assert "csv" in script
        assert "html" in script

    def test_fish_has_all_flags(self):
        script = get_completion("fish")
        assert "cli" in script
        assert "duplicates" in script
        assert "report" in script
        assert "quick" in script
        assert "api" in script
