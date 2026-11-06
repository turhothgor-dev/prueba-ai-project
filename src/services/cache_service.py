"""Cache service for storing API responses locally."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class CacheService:
    """SQLite-based cache service for API responses."""

    def __init__(self, db_path: str | Path):
        """Initialize cache service.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_key ON cache(key)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)
        """)

        conn.commit()

    def get(self, key: str) -> Any | None:
        """Get cached value by key.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT data FROM cache WHERE key = ? AND expires_at > ?",
            (key, datetime.now().isoformat()),
        )

        row = cursor.fetchone()
        if row:
            return json.loads(row["data"])

        # Clean expired entries
        self._cleanup_expired()
        return None

    def set(self, key: str, value: Any, ttl_days: int = 7) -> None:
        """Set cached value with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl_days: Time to live in days (default: 7)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        expires_at = (datetime.now() + timedelta(days=ttl_days)).isoformat()

        cursor.execute(
            """
            INSERT OR REPLACE INTO cache (key, data, expires_at)
            VALUES (?, ?, ?)
            """,
            (key, json.dumps(value), expires_at),
        )

        conn.commit()

    def delete(self, key: str) -> None:
        """Delete cached value by key.

        Args:
            key: Cache key to delete
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()

    def clear(self) -> None:
        """Clear all cached values."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache")
        conn.commit()

    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM cache WHERE expires_at <= ?",
            (datetime.now().isoformat(),),
        )
        conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
