"""Tests for DupeClean REST API."""

from __future__ import annotations

import json
import urllib.request

import pytest

from dupeclean.api import DupeCleanServer


@pytest.fixture
def server(tmp_path):
    """Start a test server on a random port."""
    import socket

    # Find a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    srv = DupeCleanServer(host="127.0.0.1", port=port)
    srv.start(background=True)
    yield srv
    srv.stop()


def _get_json(url: str) -> dict:
    """Fetch JSON from URL."""
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


class TestDupeCleanServer:
    def test_root_endpoint(self, server):
        data = _get_json(f"{server.url}/")
        assert data["name"] == "DupeClean API"
        assert data["version"] == "0.1.0"

    def test_health_endpoint(self, server):
        data = _get_json(f"{server.url}/health")
        assert data["status"] == "ok"

    def test_scan_endpoint(self, server, tmp_path):
        (tmp_path / "test.txt").write_text("hello")
        url = f"{server.url}/scan?path={tmp_path}"
        data = _get_json(url)

        assert data["summary"]["total_files"] == 1
        assert data["summary"]["total_size"] == 5

    def test_scan_nonexistent(self, server):
        url = f"{server.url}/scan?path=/nonexistent"
        try:
            _get_json(url)
            raise AssertionError("Should have raised HTTPError")
        except urllib.error.HTTPError as e:
            assert e.code == 400

    def test_not_found(self, server):
        url = f"{server.url}/nonexistent"
        try:
            _get_json(url)
            raise AssertionError("Should have raised HTTPError")
        except urllib.error.HTTPError as e:
            assert e.code == 404

    def test_scan_with_duplicates(self, server, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"same")
        (tmp_path / "b.txt").write_bytes(b"same")
        url = f"{server.url}/scan?path={tmp_path}"
        data = _get_json(url)

        assert data["summary"]["duplicate_groups"] >= 1

    def test_context_manager(self, tmp_path):
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            port = s.getsockname()[1]

        with DupeCleanServer(port=port) as srv:
            data = _get_json(f"{srv.url}/health")
            assert data["status"] == "ok"
