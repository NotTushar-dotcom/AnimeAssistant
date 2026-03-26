"""
Aara User Profile
Persistent storage for user preferences and data using SQLite.
"""

import logging
import json
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any, Optional
from datetime import datetime

from config.settings import SETTINGS

logger = logging.getLogger(__name__)


class UserProfile:
    """Manages persistent user profile data using SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize user profile storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path) if db_path else SETTINGS.data_dir / "user_profile.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Main key-value store
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS profile (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        type TEXT,
                        updated_at TEXT
                    )
                """)

                # Preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS preferences (
                        category TEXT,
                        name TEXT,
                        value TEXT,
                        updated_at TEXT,
                        PRIMARY KEY (category, name)
                    )
                """)

                # Stats table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stats (
                        stat_name TEXT PRIMARY KEY,
                        stat_value INTEGER DEFAULT 0,
                        updated_at TEXT
                    )
                """)

                # Favorite apps
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS favorite_apps (
                        app_name TEXT PRIMARY KEY,
                        usage_count INTEGER DEFAULT 0,
                        last_used TEXT
                    )
                """)

                conn.commit()
                logger.info(f"User profile database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(str(self.db_path), check_same_thread=False)

    def _serialize_value(self, value: Any) -> tuple[str, str]:
        """Serialize a value for storage."""
        if isinstance(value, (dict, list)):
            return json.dumps(value), "json"
        elif isinstance(value, bool):
            return str(value).lower(), "bool"
        elif isinstance(value, int):
            return str(value), "int"
        elif isinstance(value, float):
            return str(value), "float"
        else:
            return str(value), "str"

    def _deserialize_value(self, value: str, value_type: str) -> Any:
        """Deserialize a stored value."""
        if value_type == "json":
            return json.loads(value)
        elif value_type == "bool":
            return value.lower() == "true"
        elif value_type == "int":
            return int(value)
        elif value_type == "float":
            return float(value)
        else:
            return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a profile value.

        Args:
            key: Profile key
            default: Default value if not found

        Returns:
            Stored value or default
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT value, type FROM profile WHERE key = ?", (key,))
                    row = cursor.fetchone()

                    if row:
                        return self._deserialize_value(row[0], row[1])
                    return default

            except Exception as e:
                logger.error(f"Failed to get profile value: {e}")
                return default

    def set(self, key: str, value: Any) -> bool:
        """
        Set a profile value.

        Args:
            key: Profile key
            value: Value to store

        Returns:
            True if successful
        """
        with self._lock:
            try:
                serialized, value_type = self._serialize_value(value)
                timestamp = datetime.now().isoformat()

                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO profile (key, value, type, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (key, serialized, value_type, timestamp))
                    conn.commit()

                logger.debug(f"Set profile value: {key} = {value}")
                return True

            except Exception as e:
                logger.error(f"Failed to set profile value: {e}")
                return False

    def delete(self, key: str) -> bool:
        """
        Delete a profile value.

        Args:
            key: Profile key to delete

        Returns:
            True if successful
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM profile WHERE key = ?", (key,))
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to delete profile value: {e}")
                return False

    # Convenience methods for common profile data

    def get_name(self) -> Optional[str]:
        """Get user's name."""
        return self.get("name")

    def set_name(self, name: str) -> bool:
        """Set user's name."""
        return self.set("name", name)

    def get_preference(self, category: str, name: str, default: Any = None) -> Any:
        """Get a specific preference."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT value FROM preferences WHERE category = ? AND name = ?
                    """, (category, name))
                    row = cursor.fetchone()
                    if row:
                        return json.loads(row[0])
                    return default
            except Exception as e:
                logger.error(f"Failed to get preference: {e}")
                return default

    def set_preference(self, category: str, name: str, value: Any) -> bool:
        """Set a specific preference."""
        with self._lock:
            try:
                timestamp = datetime.now().isoformat()
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO preferences (category, name, value, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (category, name, json.dumps(value), timestamp))
                    conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to set preference: {e}")
                return False

    def increment_stat(self, stat_name: str, amount: int = 1) -> int:
        """Increment a stat counter."""
        with self._lock:
            try:
                timestamp = datetime.now().isoformat()
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO stats (stat_name, stat_value, updated_at)
                        VALUES (?, ?, ?)
                        ON CONFLICT(stat_name) DO UPDATE SET
                        stat_value = stat_value + ?,
                        updated_at = ?
                    """, (stat_name, amount, timestamp, amount, timestamp))
                    conn.commit()

                    cursor.execute("SELECT stat_value FROM stats WHERE stat_name = ?", (stat_name,))
                    row = cursor.fetchone()
                    return row[0] if row else 0
            except Exception as e:
                logger.error(f"Failed to increment stat: {e}")
                return 0

    def get_stat(self, stat_name: str) -> int:
        """Get a stat value."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT stat_value FROM stats WHERE stat_name = ?", (stat_name,))
                    row = cursor.fetchone()
                    return row[0] if row else 0
            except Exception as e:
                logger.error(f"Failed to get stat: {e}")
                return 0

    def record_app_usage(self, app_name: str) -> None:
        """Record app usage for favorites tracking."""
        with self._lock:
            try:
                timestamp = datetime.now().isoformat()
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO favorite_apps (app_name, usage_count, last_used)
                        VALUES (?, 1, ?)
                        ON CONFLICT(app_name) DO UPDATE SET
                        usage_count = usage_count + 1,
                        last_used = ?
                    """, (app_name, timestamp, timestamp))
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to record app usage: {e}")

    def get_favorite_apps(self, limit: int = 5) -> list[str]:
        """Get most frequently used apps."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT app_name FROM favorite_apps
                        ORDER BY usage_count DESC
                        LIMIT ?
                    """, (limit,))
                    rows = cursor.fetchall()
                    return [row[0] for row in rows]
            except Exception as e:
                logger.error(f"Failed to get favorite apps: {e}")
                return []

    def get_all_data(self) -> dict:
        """Get all profile data for export/display."""
        with self._lock:
            try:
                data = {"profile": {}, "preferences": {}, "stats": {}, "favorite_apps": []}

                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    # Profile
                    cursor.execute("SELECT key, value, type FROM profile")
                    for row in cursor.fetchall():
                        data["profile"][row[0]] = self._deserialize_value(row[1], row[2])

                    # Preferences
                    cursor.execute("SELECT category, name, value FROM preferences")
                    for row in cursor.fetchall():
                        if row[0] not in data["preferences"]:
                            data["preferences"][row[0]] = {}
                        data["preferences"][row[0]][row[1]] = json.loads(row[2])

                    # Stats
                    cursor.execute("SELECT stat_name, stat_value FROM stats")
                    for row in cursor.fetchall():
                        data["stats"][row[0]] = row[1]

                    # Favorite apps
                    cursor.execute("SELECT app_name, usage_count FROM favorite_apps ORDER BY usage_count DESC")
                    data["favorite_apps"] = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]

                return data

            except Exception as e:
                logger.error(f"Failed to get all data: {e}")
                return {}
