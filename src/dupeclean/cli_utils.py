"""File deduplication CLI integration module for DupeClean.

Bridge between CLI args and dedup modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .models import format_size


@dataclass
class CLIResult:
    """Result of a CLI operation."""

    success: bool
    message: str
    exit_code: int = 0
    data: dict = field(default_factory=dict)


def validate_path(path: str) -> tuple[bool, Path, str]:
    """Validate a path argument.

    Returns:
        (is_valid, resolved_path, error_message)
    """
    try:
        p = Path(path).resolve()
        if not p.exists():
            return False, p, f"Path not found: {p}"
        return True, p, ""
    except Exception as e:
        return False, Path(path), str(e)


def validate_threads(threads: int) -> tuple[bool, str]:
    """Validate thread count.

    Returns:
        (is_valid, error_message)
    """
    if threads < 1:
        return False, "Thread count must be at least 1"
    if threads > 64:
        return False, "Thread count too high (max 64)"
    return True, ""


def format_size_for_cli(size: int) -> str:
    """Format size for CLI output."""
    return format_size(size)


def build_config_from_args(args: dict) -> Config:
    """Build Config from CLI arguments."""
    config = Config()
    if "threads" in args:
        config.scanner.threads = args["threads"]
    if "follow_symlinks" in args:
        config.scanner.follow_symlinks = args["follow_symlinks"]
    if "show_hidden" in args:
        config.display.show_hidden = args["show_hidden"]
    if "ignore" in args:
        config.scanner.ignore_patterns.extend(args["ignore"])
    return config


def format_error(message: str, details: str = "") -> str:
    """Format an error message for CLI output."""
    lines = [f"Error: {message}"]
    if details:
        lines.append(f"  {details}")
    return "\n".join(lines)


def format_success(message: str, details: str = "") -> str:
    """Format a success message for CLI output."""
    lines = [f"Success: {message}"]
    if details:
        lines.append(f"  {details}")
    return "\n".join(lines)
