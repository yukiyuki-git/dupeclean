# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-27

### Added

- **Core scanning engine** with multi-threaded directory traversal
- **3-stage deduplication**: xxhash (quick) → md5 (medium) → sha256 (full)
- **Interactive TUI** built with Textual framework
  - Dashboard with summary stats
  - Largest files view
  - Duplicate groups view
  - File type distribution
  - Directory browser
  - Help screen
- **CLI mode** with `--cli`, `--top N`, `--duplicates` flags
- **Report export** in JSON, CSV, and HTML formats
- **Cleanup wizard** with delete, recycle, hardlink, move, keep-newest/oldest
- **TOML configuration** with platform-specific config paths
- **Cross-platform** support (Windows, macOS, Linux)
- **108 unit tests** covering all core modules
- **CI/CD** via GitHub Actions (test matrix: 3 OS x 4 Python versions)
- **PyPI publishing** workflow
