# Contributing to DupeClean

Thank you for your interest in contributing to DupeClean! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install in development mode

```bash
git clone https://github.com/YOUR_USERNAME/dupeclean.git
cd dupeclean
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=dupeclean --cov-report=term-missing

# Run specific test file
pytest tests/test_scanner.py -v
```

### Code Quality

```bash
# Lint check
ruff check src/ tests/

# Auto-fix lint issues
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/
```

### Quick Check

```bash
make check  # Runs lint + tests
```

## Project Structure

```
src/dupeclean/
├── cli.py          # CLI entry point
├── scanner.py      # File system scanner
├── hasher.py       # Multi-stage file hasher
├── dedup.py        # Duplicate detection
├── analyzer.py     # Analysis orchestrator
├── models.py       # Data models
├── config.py       # Configuration
├── utils.py        # Utilities
├── report.py       # Report generation
├── cleanup.py      # File cleanup
├── compare.py      # Directory comparison
├── age.py          # File age analysis
├── entropy.py      # Entropy analysis
├── watcher.py      # Directory watcher
├── ignore.py       # Ignore file support
└── tui/            # Textual TUI
    ├── app.py
    ├── themes.py
    ├── screens/
    └── widgets/
```

## Adding a New Module

1. Create `src/dupeclean/yourmodule.py`
2. Add tests in `tests/test_yourmodule.py`
3. Run `ruff check src/ tests/ --fix`
4. Run `pytest tests/test_yourmodule.py -v`
5. Update README if adding user-facing features

## Coding Guidelines

- **Python 3.10+** — use modern syntax (`X | None`, `match`, etc.)
- **Type hints** — all public functions must have type hints
- **Docstrings** — all public functions must have docstrings
- **Tests** — every module needs tests
- **Ruff** — all code must pass `ruff check`
- **Line length** — 100 characters max (except HTML templates)

## Submitting Changes

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Make your changes
3. Run `make check` to ensure everything passes
4. Commit with a descriptive message
5. Push to your fork
6. Open a Pull Request

### Commit Messages

Use conventional commits:

- `feat: add new feature`
- `fix: fix a bug`
- `docs: update documentation`
- `test: add tests`
- `refactor: refactor code`
- `chore: maintenance tasks`

## Reporting Bugs

Please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error output (if any)

## Feature Requests

Open an issue with:

- Clear description of the feature
- Use case / motivation
- Proposed implementation (if any)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
