"""Tests for DupeClean file rule engine."""

from __future__ import annotations

import time
from pathlib import Path

from dupeclean.models import FileInfo
from dupeclean.rules import (
    Rule,
    RuleMatch,
    RuleResult,
    create_age_rule,
    create_extension_rule,
    create_pattern_rule,
    create_size_rule,
    evaluate_rules,
    format_rule_result,
)


def _fi(path: str, size: int = 100, mtime: float = 0) -> FileInfo:
    return FileInfo(path=Path(path), size=size, mtime=mtime)


class TestCreateExtensionRule:
    def test_basic(self):
        rule = create_extension_rule("images", [".jpg", ".png"], "archive")
        assert rule.matches(_fi("/photo.jpg")) is True
        assert rule.matches(_fi("/code.py")) is False

    def test_case_insensitive(self):
        rule = create_extension_rule("images", [".JPG"], "archive")
        assert rule.matches(_fi("/photo.jpg")) is True


class TestCreateSizeRule:
    def test_min_size(self):
        rule = create_size_rule("large", min_size=1000, action="flag")
        assert rule.matches(_fi("/big", 2000)) is True
        assert rule.matches(_fi("/small", 500)) is False

    def test_max_size(self):
        rule = create_size_rule("small", max_size=1000, action="flag")
        assert rule.matches(_fi("/tiny", 500)) is True
        assert rule.matches(_fi("/big", 2000)) is False


class TestCreateAgeRule:
    def test_old_files(self):
        old_time = time.time() - (400 * 86400)
        rule = create_age_rule("old", min_age_days=365, action="archive")
        assert rule.matches(_fi("/old", mtime=old_time)) is True
        assert rule.matches(_fi("/new", mtime=time.time())) is False


class TestCreatePatternRule:
    def test_glob(self):
        rule = create_pattern_rule("temp", "*.tmp", "delete")
        assert rule.matches(_fi("/data.tmp")) is True
        assert rule.matches(_fi("/data.txt")) is False


class TestEvaluateRules:
    def test_basic(self):
        files = [
            _fi("/code.py", 50000),
            _fi("/photo.jpg", 5000),
            _fi("/data.tmp", 100),
        ]
        rules = [
            create_extension_rule("code", [".py"], "compress"),
            create_extension_rule("images", [".jpg"], "archive"),
            create_extension_rule("temp", [".tmp"], "delete"),
        ]
        result = evaluate_rules(files, rules)
        assert result.match_count == 3

    def test_no_matches(self):
        files = [_fi("/normal.txt")]
        rules = [
            create_extension_rule("code", [".py"], "compress"),
        ]
        result = evaluate_rules(files, rules)
        assert result.match_count == 0

    def test_multiple_rules_same_file(self):
        files = [_fi("/big.py", 100000)]
        rules = [
            create_extension_rule("code", [".py"], "compress"),
            create_size_rule("large", min_size=50000, action="flag"),
        ]
        result = evaluate_rules(files, rules)
        assert result.match_count == 2


class TestRuleResult:
    def test_match_count(self):
        result = RuleResult(
            matches=[
                RuleMatch(
                    file=_fi("/a"),
                    rule=Rule(name="test", description="", conditions=[], action="flag"),
                ),
            ]
        )
        assert result.match_count == 1


class TestFormatRuleResult:
    def test_no_matches(self):
        result = RuleResult(rules_evaluated=2, files_evaluated=10)
        assert "No matches" in format_rule_result(result)

    def test_with_matches(self):
        rule = Rule(
            name="test_rule",
            description="test",
            conditions=[],
            action="compress",
        )
        result = RuleResult(
            matches=[
                RuleMatch(file=_fi("/code.py", 50000), rule=rule),
                RuleMatch(file=_fi("/app.py", 30000), rule=rule),
            ],
            rules_evaluated=1,
            files_evaluated=10,
        )
        text = format_rule_result(result)
        assert "COMPRESS" in text
        assert "test_rule" in text
