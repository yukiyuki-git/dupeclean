"""REST API server for DupeClean.

Provides an HTTP API for remote disk analysis.
Built with Python's http.server module (no dependencies).
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from .analyzer import Analyzer
from .config import Config
from .models import format_size


class DupeCleanHandler(BaseHTTPRequestHandler):
    """HTTP request handler for DupeClean API."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/" or self.path == "":
            self._serve_dashboard()
        elif self.path == "/api":
            self._json_response(
                {
                    "name": "DupeClean API",
                    "version": "0.1.0",
                    "endpoints": [
                        "GET / — Web dashboard",
                        "GET /api — This info",
                        "GET /scan?path=<path> — Scan directory",
                        "GET /health — Health check",
                    ],
                }
            )
        elif self.path == "/health":
            self._json_response({"status": "ok"})
        elif self.path.startswith("/scan"):
            self._handle_scan()
        else:
            self._error_response(404, "Not found")

    def _serve_dashboard(self) -> None:
        """Serve the web dashboard HTML."""
        dashboard_path = Path(__file__).parent / "static" / "dashboard.html"
        if dashboard_path.exists():
            content = dashboard_path.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode())
        else:
            self._json_response(
                {
                    "name": "DupeClean API",
                    "version": "0.1.0",
                    "message": "Dashboard not found. Visit /api for API info.",
                }
            )

    def _handle_scan(self) -> None:
        """Handle scan request."""
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        path_str = params.get("path", ["."])[0]
        path = Path(path_str).resolve()

        if not path.exists():
            self._error_response(400, f"Path not found: {path}")
            return

        try:
            config = Config()
            analyzer = Analyzer(config)
            result = analyzer.analyze(path)

            response = {
                "directory": str(result.root),
                "summary": {
                    "total_size": result.stats.total_size,
                    "total_size_display": format_size(result.stats.total_size),
                    "total_files": result.stats.total_files,
                    "total_dirs": result.stats.total_dirs,
                    "duplicate_groups": result.stats.duplicate_groups,
                    "duplicate_files": result.stats.duplicate_files,
                    "wasted_space": result.stats.wasted_space,
                    "scan_duration": round(result.stats.scan_duration, 3),
                },
                "top_files": [
                    {
                        "path": str(f.path),
                        "size": f.size,
                        "size_display": f.size_display,
                    }
                    for f in result.largest_files[:20]
                ],
                "duplicates": [
                    {
                        "group_id": g.group_id,
                        "count": g.count,
                        "file_size": g.file_size,
                        "wasted_space": g.wasted_space,
                        "files": [str(f.path) for f in g.files],
                    }
                    for g in result.top_duplicates[:20]
                ],
            }
            self._json_response(response)

        except Exception as e:
            self._error_response(500, str(e))

    def _json_response(self, data: Any, status: int = 200) -> None:
        """Send a JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _error_response(self, status: int, message: str) -> None:
        """Send an error response."""
        self._json_response({"error": message}, status)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging."""
        pass


class DupeCleanServer:
    """DupeClean REST API server."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self, background: bool = True) -> None:
        """Start the server.

        Args:
            background: Run in a background thread.
        """
        self._server = HTTPServer((self.host, self.port), DupeCleanHandler)

        if background:
            self._thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True,
            )
            self._thread.start()
        else:
            self._server.serve_forever()

    def stop(self) -> None:
        """Stop the server."""
        if self._server:
            self._server.shutdown()
            self._server = None

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def __enter__(self) -> DupeCleanServer:
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop()
