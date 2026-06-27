"""File rule engine for DupeClean.

Define and evaluate rules for automated file management.
"""

from __future__ import annotations

import fnmatch
from collections.abc import Callable
from dataclasses import dataclass, field

from .models import FileInfo


@dataclass
class Rule:
    """A file management rule."""

    name: str
    description: str
    conditions: list[Callable[[FileInfo], bool]]
    action: str  # "tag", "move", "delete", "compress", "archive"
    action_args: dict = field(default_factory=dict)
    priority: int = 0

    def matches(self, fi: FileInfo) -> bool:
        """Check if a file matches all conditions."""
        return all(cond(fi) for cond in self.conditions)


@dataclass
class RuleMatch:
    """A file that matches a rule."""

    file: FileInfo
    rule: Rule


@dataclass
class RuleResult:
    """Results of rule evaluation."""

    matches: list[RuleMatch] = field(default_factory=list)
    rules_evaluated: int = 0
    files_evaluated: int = 0

    @property
    def match_count(self) -> int:
        return len(self.matches)


def create_extension_rule(
    name: str,
    extensions: list[str],
    action: str,
    description: str = "",
    **action_args,
) -> Rule:
    """Create a rule matching files by extension."""
    ext_set = {e.lstrip(".").lower() for e in extensions}
    return Rule(
        name=name,
        description=description or f"Match {extensions}",
        conditions=[lambda fi: fi.ext.lstrip(".").lower() in ext_set],
        action=action,
        action_args=action_args,
    )


def create_size_rule(
    name: str,
    min_size: int = 0,
    max_size: int = 0,
    action: str = "flag",
    description: str = "",
    **action_args,
) -> Rule:
    """Create a rule matching files by size."""

    def size_check(fi: FileInfo) -> bool:
        if min_size > 0 and fi.size < min_size:
            return False
        return not (max_size > 0 and fi.size > max_size)

    return Rule(
        name=name,
        description=description or f"Size {min_size}-{max_size}",
        conditions=[size_check],
        action=action,
        action_args=action_args,
    )


def create_age_rule(
    name: str,
    min_age_days: float = 0,
    max_age_days: float = 0,
    action: str = "archive",
    description: str = "",
    **action_args,
) -> Rule:
    """Create a rule matching files by age."""
    import time

    def age_check(fi: FileInfo) -> bool:
        age_days = (time.time() - fi.mtime) / 86400
        if min_age_days > 0 and age_days < min_age_days:
            return False
        return not (max_age_days > 0 and age_days > max_age_days)

    return Rule(
        name=name,
        description=description or f"Age {min_age_days}-{max_age_days}d",
        conditions=[age_check],
        action=action,
        action_args=action_args,
    )


def create_pattern_rule(
    name: str,
    pattern: str,
    action: str,
    description: str = "",
    **action_args,
) -> Rule:
    """Create a rule matching files by name pattern."""
    return Rule(
        name=name,
        description=description or f"Pattern {pattern}",
        conditions=[lambda fi: fnmatch.fnmatch(fi.path.name, pattern)],
        action=action,
        action_args=action_args,
    )


def evaluate_rules(
    files: list[FileInfo],
    rules: list[Rule],
) -> RuleResult:
    """Evaluate rules against files.

    Returns:
        RuleResult with all matches.
    """
    result = RuleResult(
        rules_evaluated=len(rules),
        files_evaluated=len(files),
    )

    for fi in files:
        for rule in rules:
            if rule.matches(fi):
                result.matches.append(RuleMatch(file=fi, rule=rule))

    result.matches.sort(key=lambda m: (m.rule.priority, -m.file.size))
    return result


def format_rule_result(result: RuleResult) -> str:
    """Format rule evaluation results as text."""
    if not result.matches:
        return (
            f"No matches ({result.rules_evaluated} rules, "
            f"{result.files_evaluated:,} files evaluated)."
        )

    lines = [
        f"Rule Results: {result.match_count:,} matches "
        f"({result.rules_evaluated} rules, "
        f"{result.files_evaluated:,} files)",
        "",
    ]

    # Group by rule
    by_rule: dict[str, list[RuleMatch]] = {}
    for match in result.matches:
        by_rule.setdefault(match.rule.name, []).append(match)

    for rule_name, matches in by_rule.items():
        rule = matches[0].rule
        lines.append(f"  [{rule.action.upper()}] {rule_name}: {len(matches)} files")
        for m in matches[:3]:
            lines.append(f"    {m.file.size_display:>10s}  {m.file.path.name}")
        if len(matches) > 3:
            lines.append(f"    ... and {len(matches) - 3} more")
        lines.append("")

    return "\n".join(lines)
