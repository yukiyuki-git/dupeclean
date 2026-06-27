"""CLI entry point for DupeClean."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __app_name__, __version__
from .config import Config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dupeclean",
        description=f"{__app_name__} — Smart disk analyzer & duplicate file finder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  dupeclean                      Analyze current directory (TUI mode)
  dupeclean /path/to/dir         Analyze specific path
  dupeclean --duplicates /path   Find duplicates only
  dupeclean --report html        Generate HTML report
  dupeclean --cli /path          CLI mode (no TUI)
  dupeclean --top 20 /path       Show top 20 largest files
        """,
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"{__app_name__} {__version__}"
    )

    mode = parser.add_argument_group("mode")
    mode.add_argument("--cli", action="store_true", help="Run in CLI mode (no TUI)")
    mode.add_argument(
        "--duplicates", "-d", action="store_true", help="Find and show duplicate files"
    )
    mode.add_argument("--top", "-t", type=int, metavar="N", help="Show top N largest files")
    mode.add_argument(
        "--compare",
        nargs=2,
        metavar=("DIR_A", "DIR_B"),
        help="Compare two directories",
    )
    mode.add_argument(
        "--report", choices=["json", "csv", "html"], metavar="FORMAT", help="Generate report"
    )
    mode.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick scan (size-based, no hashing)",
    )
    mode.add_argument(
        "--api",
        action="store_true",
        help="Start REST API server",
    )
    mode.add_argument(
        "--api-port",
        type=int,
        default=8080,
        metavar="PORT",
        help="API server port (default: 8080)",
    )
    mode.add_argument("--health", action="store_true", help="Disk health check")
    mode.add_argument("--forecast", action="store_true", help="Disk space forecast")
    mode.add_argument("--entropy", action="store_true", help="File entropy analysis")
    mode.add_argument("--treemap", action="store_true", help="Show disk usage treemap")
    mode.add_argument("--fuzzy", action="store_true", help="Find similar filenames")
    mode.add_argument("--search", metavar="PATTERN", help="Search files by name pattern")

    options = parser.add_argument_group("options")
    options.add_argument("--output", "-o", type=Path, metavar="FILE", help="Output file for report")
    options.add_argument(
        "--threads", type=int, default=4, metavar="N", help="Number of threads (default: 4)"
    )
    options.add_argument("--follow-symlinks", action="store_true", help="Follow symbolic links")
    options.add_argument("--show-hidden", action="store_true", help="Include hidden files")
    options.add_argument(
        "--ignore", nargs="+", metavar="PATTERN", help="Additional glob patterns to ignore"
    )
    options.add_argument("--no-dedup", action="store_true", help="Skip duplicate detection")
    options.add_argument("--config", type=Path, metavar="FILE", help="Path to config file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = Config.load(args.config)
    config.scanner.threads = args.threads
    config.scanner.follow_symlinks = args.follow_symlinks
    config.display.show_hidden = args.show_hidden
    if args.ignore:
        config.scanner.ignore_patterns.extend(args.ignore)

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"Error: Path not found: {target}", file=sys.stderr)
        return 1

    if args.report:
        return _run_report(target, args.report, args.output, args.no_dedup, config)
    if args.compare:
        return _run_compare(args.compare[0], args.compare[1], config)
    if args.api:
        return _run_api(target, args.api_port, config)
    if args.quick:
        return _run_quick(target, config)
    if args.health:
        return _run_health(target)
    if args.forecast:
        return _run_forecast(target)
    if args.entropy:
        return _run_entropy(target, config)
    if args.treemap:
        return _run_treemap(target, config)
    if args.fuzzy:
        return _run_fuzzy(target, config)
    if args.search:
        return _run_search(target, args.search, config)
    if args.cli or args.top or args.duplicates:
        return _run_cli(target, args, config)
    return _run_tui(target, config)


def _run_tui(target: Path, config: Config) -> int:
    try:
        from .tui.app import DupeCleanApp

        app = DupeCleanApp(target, config)
        app.run()
        return 0
    except ImportError as e:
        print(f"Error: TUI dependencies not installed: {e}", file=sys.stderr)
        return _run_cli_fallback(target, config)


def _run_cli(target: Path, args: argparse.Namespace, config: Config) -> int:
    from .analyzer import Analyzer
    from .models import format_size

    analyzer = Analyzer(config)
    analyzer.on_progress(lambda msg, done, total: print(f"\r{msg}", end="", flush=True))
    result = analyzer.analyze(target, find_dupes=not args.no_dedup)
    print()
    if args.top:
        print(f"\nTop {args.top} largest files in {target}:\n")
        for i, fi in enumerate(result.largest_files[: args.top], 1):
            print(f"  {i:>4}. {fi.size_display:>10s}  {fi.path}")
        print()
        return 0
    if args.duplicates:
        groups = result.top_duplicates
        if not groups:
            print("No duplicate files found.")
            return 0
        print(
            f"\nFound {len(groups)} duplicate groups "
            f"({result.stats.duplicate_files} files, "
            f"{format_size(result.stats.wasted_space)} wasted):\n"
        )
        for g in groups[:50]:
            print(
                f"  Group #{g.group_id}: {g.count} files x "
                f"{g.size_display} (wasted: {g.wasted_display})"
            )
            for fi in g.files:
                print(f"    {fi.path}")
        if len(groups) > 50:
            print(f"\n  ... and {len(groups) - 50} more groups")
        print()
        return 0
    print(result.summary_text())
    return 0


def _run_compare(dir_a: str, dir_b: str, config: Config) -> int:
    from .compare import compare_directories

    path_a = Path(dir_a).resolve()
    path_b = Path(dir_b).resolve()
    if not path_a.exists():
        print(f"Error: Path not found: {path_a}", file=sys.stderr)
        return 1
    if not path_b.exists():
        print(f"Error: Path not found: {path_b}", file=sys.stderr)
        return 1

    print(f"Comparing {path_a} vs {path_b}...\n")
    result = compare_directories(path_a, path_b, config)
    print(result.summary_text())

    if result.only_in_a:
        print(f"\n  Only in {path_a}:")
        for fi in result.only_in_a[:20]:
            print(f"    {fi.size_display:>10s}  {fi.path.name}")

    if result.only_in_b:
        print(f"\n  Only in {path_b}:")
        for fi in result.only_in_b[:20]:
            print(f"    {fi.size_display:>10s}  {fi.path.name}")

    if result.modified:
        print(f"\n  Modified ({len(result.modified)} files):")
        for fa, fb in result.modified[:20]:
            print(f"    {fa.path.name}: {fa.size_display} -> {fb.size_display}")

    return 0


def _run_quick(target: Path, config: Config) -> int:
    from .quickscan import format_quick_scan_result, quick_scan

    files, stats, groups = quick_scan(target, config)
    print(format_quick_scan_result(target, files, stats, groups))
    return 0


def _run_api(target: Path, port: int, config: Config) -> int:
    from .api import DupeCleanServer

    print(f"Starting DupeClean API server on port {port}...")
    print(f"  Scan target: {target}")
    print(f"  API URL: http://127.0.0.1:{port}/")
    print("  Press Ctrl+C to stop\n")

    server = DupeCleanServer(port=port)
    try:
        server.start(background=False)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    return 0


def _run_health(target: Path) -> int:
    from .health import check_disk_health, format_health_report

    report = check_disk_health(target)
    print(format_health_report(report))
    return 0


def _run_forecast(target: Path) -> int:
    from .forecast import forecast_disk_space, format_forecast

    forecast = forecast_disk_space(target)
    print(format_forecast(forecast))
    return 0


def _run_entropy(target: Path, config: Config) -> int:
    from .analyzer import Analyzer
    from .entropy import find_high_entropy_files

    analyzer = Analyzer(config)
    result = analyzer.analyze(target, find_dupes=False)
    high_ent = find_high_entropy_files(result.files)

    if not high_ent:
        print("No high-entropy files found.")
        return 0

    print(f"\nHigh entropy files ({len(high_ent)}):\n")
    for ent in high_ent[:30]:
        print(f"  {ent.entropy:.2f}  {ent.size_display:>10s}  [{ent.category}]  {ent.path.name}")
    return 0


def _run_treemap(target: Path, config: Config) -> int:
    from .analyzer import Analyzer
    from .treemap import build_treemap, format_treemap

    analyzer = Analyzer(config)
    result = analyzer.analyze(target, find_dupes=False)
    node = build_treemap(result.dirs, target)
    print(format_treemap(node))
    return 0


def _run_fuzzy(target: Path, config: Config) -> int:
    from .analyzer import Analyzer
    from .fuzzy import find_similar_names

    analyzer = Analyzer(config)
    result = analyzer.analyze(target, find_dupes=False)
    groups = find_similar_names(result.files)

    if not groups:
        print("No similar filenames found.")
        return 0

    print(f"\nSimilar filename groups ({len(groups)}):\n")
    for g in groups[:20]:
        print(f"  Group #{g.group_id}: {g.count} files (similarity: {g.similarity:.0%})")
        for fi in g.files:
            print(f"    {fi.path.name}")
    return 0


def _run_search(target: Path, pattern: str, config: Config) -> int:
    from .analyzer import Analyzer
    from .search import SearchQuery, format_search_result, search_files

    analyzer = Analyzer(config)
    result = analyzer.analyze(target, find_dupes=False)
    query = SearchQuery(name_pattern=pattern)
    search_result = search_files(result.files, query)
    print(format_search_result(search_result))
    return 0


def _run_report(
    target: Path, format: str, output: Path | None, no_dedup: bool, config: Config
) -> int:
    from .analyzer import Analyzer
    from .report import ReportGenerator

    analyzer = Analyzer(config)
    result = analyzer.analyze(target, find_dupes=not no_dedup)
    gen = ReportGenerator(result)
    content = gen.generate(format, output)
    if content and not output:
        print(content)
    elif output:
        print(f"Report saved to: {output}")
    return 0


def _run_cli_fallback(target: Path, config: Config) -> int:
    from .analyzer import Analyzer

    print(f"Analyzing {target}...\n")
    analyzer = Analyzer(config)
    result = analyzer.analyze(target)
    print(result.summary_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
