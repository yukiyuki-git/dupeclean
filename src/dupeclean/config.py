"""Configuration management for DupeClean."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CONFIG_FILE_NAME = "config.toml"
APP_DIR_NAME = "dupeclean"


@dataclass
class ScannerConfig:
    follow_symlinks: bool = False
    skip_hidden: bool = False
    threads: int = 4
    ignore_patterns: list[str] = field(default_factory=lambda: [
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
        "dist", "build", ".eggs",
    ])


@dataclass
class HasherConfig:
    quick_hash_size: int = 4096
    medium_hash_size: int = 65536
    algorithm: str = "xxhash"


@dataclass
class DisplayConfig:
    size_format: str = "binary"
    theme: str = "default"
    show_hidden: bool = False


@dataclass
class Config:
    scanner: ScannerConfig = field(default_factory=ScannerConfig)
    hasher: HasherConfig = field(default_factory=HasherConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> Config:
        if path is None:
            path = get_config_path()
        if path and path.exists():
            return cls._from_toml(path)
        return cls()

    @classmethod
    def _from_toml(cls, path: Path) -> Config:
        config = cls()
        try:
            import tomllib
        except ModuleNotFoundError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ModuleNotFoundError:
                return config
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            return config
        if "scanner" in data:
            s = data["scanner"]
            for key in ("follow_symlinks", "skip_hidden", "threads", "ignore_patterns"):
                if key in s:
                    setattr(config.scanner, key, s[key])
        if "hasher" in data:
            h = data["hasher"]
            for key in ("quick_hash_size", "medium_hash_size", "algorithm"):
                if key in h:
                    setattr(config.hasher, key, h[key])
        if "display" in data:
            d = data["display"]
            for key in ("size_format", "theme", "show_hidden"):
                if key in d:
                    setattr(config.display, key, d[key])
        return config

    def save(self, path: Optional[Path] = None) -> None:
        if path is None:
            path = get_config_path()
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "[scanner]",
            f"follow_symlinks = {str(self.scanner.follow_symlinks).lower()}",
            f"skip_hidden = {str(self.scanner.skip_hidden).lower()}",
            f"threads = {self.scanner.threads}",
            f"ignore_patterns = {self.scanner.ignore_patterns!r}",
            "",
            "[hasher]",
            f"quick_hash_size = {self.hasher.quick_hash_size}",
            f"medium_hash_size = {self.hasher.medium_hash_size}",
            f'algorithm = "{self.hasher.algorithm}"',
            "",
            "[display]",
            f'size_format = "{self.display.size_format}"',
            f'theme = "{self.display.theme}"',
            f"show_hidden = {str(self.display.show_hidden).lower()}",
        ]
        path.write_text("\n".join(lines) + "\n")


def get_config_path() -> Optional[Path]:
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA")
        if app_data:
            return Path(app_data) / APP_DIR_NAME / CONFIG_FILE_NAME
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / APP_DIR_NAME / CONFIG_FILE_NAME
        home = Path.home()
        return home / ".config" / APP_DIR_NAME / CONFIG_FILE_NAME
    return Path.home() / f".{APP_DIR_NAME}" / CONFIG_FILE_NAME


def get_data_path() -> Path:
    if sys.platform == "win32":
        app_data = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        if app_data:
            return Path(app_data) / APP_DIR_NAME
    else:
        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache:
            return Path(xdg_cache) / APP_DIR_NAME
        return Path.home() / ".cache" / APP_DIR_NAME
    return Path.home() / f".{APP_DIR_NAME}"
