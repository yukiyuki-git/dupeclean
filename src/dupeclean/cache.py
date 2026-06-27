"""SQLite cache for incremental scans in DupeClean.

Stores scan results in a SQLite database so subsequent scans
can skip files that haven't changed (same size + mtime).
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .models import FileInfo

DB_FILE_NAME = "dupeclean_cache.db"


@dataclass
class CacheEntry:
    """A cached file entry."""
    path: str
    size: int
    mtime: float
    quick_hash: str | None
    medium_hash: str | None
    full_hash: str | None
    scan_time: float


class ScanCache:
    """SQLite-backed scan cache.

    Stores file metadata and hashes so that subsequent scans
    can reuse results for unchanged files.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            db_path = Path(DB_FILE_NAME)
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def open(self) -> None:
        """Open the database connection."""
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._create_tables()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> ScanCache:
        self.open()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _create_tables(self) -> None:
        assert self._conn is not None
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                size INTEGER NOT NULL,
                mtime REAL NOT NULL,
                quick_hash TEXT,
                medium_hash TEXT,
                full_hash TEXT,
                scan_time REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_size ON files(size);
            CREATE INDEX IF NOT EXISTS idx_mtime ON files(mtime);
            CREATE INDEX IF NOT EXISTS idx_quick_hash
                ON files(quick_hash);
            CREATE INDEX IF NOT EXISTS idx_full_hash
                ON files(full_hash);

            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_path TEXT NOT NULL,
                scan_time REAL NOT NULL,
                total_files INTEGER,
                total_size INTEGER,
                duplicate_groups INTEGER,
                wasted_space INTEGER
            );
        """)

    def get(self, path: Path) -> CacheEntry | None:
        """Get cached entry for a file."""
        assert self._conn is not None
        row = self._conn.execute(
            "SELECT path, size, mtime, quick_hash, medium_hash, "
            "full_hash, scan_time FROM files WHERE path = ?",
            (str(path),),
        ).fetchone()
        if row is None:
            return None
        return CacheEntry(
            path=row[0],
            size=row[1],
            mtime=row[2],
            quick_hash=row[3],
            medium_hash=row[4],
            full_hash=row[5],
            scan_time=row[6],
        )

    def is_cached(self, path: Path, size: int, mtime: float) -> bool:
        """Check if a file is cached and unchanged."""
        entry = self.get(path)
        if entry is None:
            return False
        return entry.size == size and entry.mtime == mtime

    def put(self, fi: FileInfo) -> None:
        """Cache a file's metadata and hashes."""
        assert self._conn is not None
        self._conn.execute(
            "INSERT OR REPLACE INTO files "
            "(path, size, mtime, quick_hash, medium_hash, "
            "full_hash, scan_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(fi.path),
                fi.size,
                fi.mtime,
                fi.quick_hash,
                fi.medium_hash,
                fi.full_hash,
                time.time(),
            ),
        )

    def put_batch(self, files: list[FileInfo]) -> None:
        """Cache multiple files in a single transaction."""
        assert self._conn is not None
        now = time.time()
        rows = [
            (
                str(fi.path),
                fi.size,
                fi.mtime,
                fi.quick_hash,
                fi.medium_hash,
                fi.full_hash,
                now,
            )
            for fi in files
        ]
        self._conn.executemany(
            "INSERT OR REPLACE INTO files "
            "(path, size, mtime, quick_hash, medium_hash, "
            "full_hash, scan_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        self._conn.commit()

    def get_uncached(
        self, files: list[FileInfo]
    ) -> list[FileInfo]:
        """Filter files to only those not in cache or changed."""
        result = []
        for fi in files:
            if not self.is_cached(fi.path, fi.size, fi.mtime):
                result.append(fi)
            else:
                # Restore cached hashes
                entry = self.get(fi.path)
                if entry:
                    fi.quick_hash = entry.quick_hash
                    fi.medium_hash = entry.medium_hash
                    fi.full_hash = entry.full_hash
        return result

    def apply_cached_hashes(self, files: list[FileInfo]) -> int:
        """Apply cached hashes to files. Returns count of cache hits."""
        hits = 0
        for fi in files:
            entry = self.get(fi.path)
            if (
                entry
                and entry.size == fi.size
                and entry.mtime == fi.mtime
            ):
                fi.quick_hash = entry.quick_hash
                fi.medium_hash = entry.medium_hash
                fi.full_hash = entry.full_hash
                hits += 1
        return hits

    def record_scan(
        self,
        root: str,
        total_files: int,
        total_size: int,
        duplicate_groups: int,
        wasted_space: int,
    ) -> None:
        """Record a scan in the history table."""
        assert self._conn is not None
        self._conn.execute(
            "INSERT INTO scans "
            "(root_path, scan_time, total_files, total_size, "
            "duplicate_groups, wasted_space) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                root,
                time.time(),
                total_files,
                total_size,
                duplicate_groups,
                wasted_space,
            ),
        )
        self._conn.commit()

    def get_scan_history(
        self, root: str | None = None, limit: int = 20
    ) -> list[dict]:
        """Get scan history."""
        assert self._conn is not None
        if root:
            rows = self._conn.execute(
                "SELECT root_path, scan_time, total_files, "
                "total_size, duplicate_groups, wasted_space "
                "FROM scans WHERE root_path = ? "
                "ORDER BY scan_time DESC LIMIT ?",
                (root, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT root_path, scan_time, total_files, "
                "total_size, duplicate_groups, wasted_space "
                "FROM scans ORDER BY scan_time DESC LIMIT ?",
                (limit,),
            ).fetchall()

        return [
            {
                "root": r[0],
                "time": r[1],
                "files": r[2],
                "size": r[3],
                "dup_groups": r[4],
                "wasted": r[5],
            }
            for r in rows
        ]

    def purge_old(self, max_age_days: float = 30) -> int:
        """Remove cache entries older than max_age_days."""
        assert self._conn is not None
        cutoff = time.time() - (max_age_days * 86400)
        cursor = self._conn.execute(
            "DELETE FROM files WHERE scan_time < ?", (cutoff,)
        )
        self._conn.commit()
        return cursor.rowcount

    def clear(self) -> None:
        """Clear all cache data."""
        assert self._conn is not None
        self._conn.executescript(
            "DELETE FROM files; DELETE FROM scans;"
        )
        self._conn.commit()

    def stats(self) -> dict:
        """Get cache statistics."""
        assert self._conn is not None
        file_count = self._conn.execute(
            "SELECT COUNT(*) FROM files"
        ).fetchone()[0]
        scan_count = self._conn.execute(
            "SELECT COUNT(*) FROM scans"
        ).fetchone()[0]
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        return {
            "cached_files": file_count,
            "scan_history": scan_count,
            "db_size_bytes": db_size,
        }
