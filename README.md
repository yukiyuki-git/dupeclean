# DupeClean

<p align="center">
  <strong>🔍 Smart disk analyzer & duplicate file finder with a modern TUI</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/TUI-Textual-purple.svg" alt="Textual TUI">
</p>

DupeClean is a fast, modern terminal tool for analyzing disk usage and finding duplicate files. It combines the directory-navigation power of `ncdu` with intelligent duplicate detection and a beautiful interactive TUI.

## ✨ Features

- **📊 Disk Usage Analysis** — Interactive directory tree sorted by size
- **🔍 Smart Deduplication** — Multi-stage hashing (xxhash → MD5 → SHA256) for fast, accurate detection
- **🗂️ File Type Statistics** — Visual breakdown of space by file type
- **📦 Large File Finder** — Quickly identify space hogs
- **🧹 Cleanup Wizard** — Safely remove, move, or hardlink duplicates
- **📈 Report Export** — Generate JSON, CSV, or HTML reports
- **⚡ Blazing Fast** — Multi-threaded scanning with incremental updates
- **🖱️ Full TUI** — Mouse support, keyboard shortcuts, and smooth animations

## 📦 Installation

```bash
pip install dupeclean
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install dupeclean
```

## 🚀 Usage

```bash
# Analyze current directory (TUI mode)
dupeclean

# Analyze a specific path
dupeclean /path/to/analyze

# Find duplicates only
dupeclean --duplicates /path

# Show top 20 largest files
dupeclean --top 20 /path

# Generate HTML report
dupeclean --report html /path

# CLI mode (no TUI)
dupeclean --cli /path
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate |
| `Enter` | Open directory / Select |
| `Backspace` | Go up |
| `d` | Toggle duplicate view |
| `s` | Sort by size |
| `n` | Sort by name |
| `D` | Mark for deletion |
| `x` | Execute cleanup |
| `r` | Refresh |
| `q` | Quit |
| `?` | Help |

## 🏗️ Architecture

```
src/dupeclean/
├── cli.py              # CLI entry point
├── scanner.py          # File system scanner
├── hasher.py           # Multi-stage file hasher
├── dedup.py            # Duplicate detection engine
├── analyzer.py         # High-level analysis orchestrator
├── models.py           # Data models
├── report.py           # Report generation (JSON/CSV/HTML)
├── cleanup.py          # Safe file cleanup operations
├── config.py           # Configuration management
├── utils.py            # Utility functions
└── tui/
    ├── app.py          # Main Textual app
    ├── themes.py       # Color themes
    ├── screens/
    │   ├── main.py     # Main dashboard screen
    │   ├── browse.py   # Directory browser screen
    │   ├── duplicates.py # Duplicate groups screen
    │   ├── treemap.py  # Treemap visualization
    │   ├── stats.py    # Statistics screen
    │   └── help.py     # Help screen
    └── widgets/
        ├── header.py   # Custom header
        ├── footer.py   # Custom footer
        ├── tree_view.py # Directory tree widget
        ├── file_table.py # File listing table
        ├── progress.py # Progress bar widget
        ├── chart.py    # Chart widgets
        └── confirm.py  # Confirmation dialog
```

## ⚙️ Configuration

DupeClean looks for configuration in:
- `~/.config/dupeclean/config.toml` (Linux/macOS)
- `%APPDATA%/dupeclean/config.toml` (Windows)

```toml
[scanner]
follow_symlinks = false
skip_hidden = false
threads = 4
ignore_patterns = [".git", "node_modules", "__pycache__", ".venv"]

[hasher]
quick_hash_size = 4096    # bytes for quick hash (stage 1)
medium_hash_size = 65536  # bytes for medium hash (stage 2)
algorithm = "xxhash"      # xxhash, md5, sha256

[display]
size_format = "binary"    # binary (1024) or decimal (1000)
theme = "default"
show_hidden = false
```

## 🧪 Development

```bash
git clone https://github.com/user/dupeclean.git
cd dupeclean
pip install -e ".[dev]"
pytest
ruff check src/ tests/
```

## 📋 Roadmap

- [x] Core scanning engine
- [x] Multi-stage deduplication
- [x] Interactive TUI
- [x] Report export
- [x] Cleanup wizard
- [ ] Watch mode (monitor changes)
- [ ] Plugin system
- [ ] Cloud storage support (S3, GCS)
- [ ] SQLite cache for incremental scans

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Textual](https://textual.textualize.io/) — Modern TUI framework
- [Rich](https://rich.readthedocs.io/) — Terminal formatting
- [ncdu](https://dev.yorhel.nl/ncdu) — Inspiration for the disk usage interface
- [fclones](https://github.com/pkolaczk/fclones) — Inspiration for dedup strategy
