from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any

import json
import re
import sqlite3


@dataclass(slots=True)
class UserRecord:
    user_id: int
    social_score: int
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class UserDatabase:
    _COLUMN_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    USER_COLUMN_MIGRATIONS: list[tuple[str, str]] = [
        # Add new per-user fields here.
        # ("llm_context", "TEXT NOT NULL DEFAULT ''"),
    ]

    def __init__(self, db_path: str | Path = "db.sqlite3") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = RLock()
        self._connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row

        self._initialise_schema()
        self._apply_migrations()

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def _initialise_schema(self) -> None:
        with self._lock:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    is_supreme_leader BOOLEAN NOT NULL DEFAULT 0,
                    social_score INTEGER NOT NULL DEFAULT 0,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self._connection.execute(
                """
                CREATE TRIGGER IF NOT EXISTS users_set_updated_at
                AFTER UPDATE ON users
                FOR EACH ROW
                BEGIN
                    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = OLD.user_id;
                END
                """
            )
            self._connection.commit()

    def _apply_migrations(self) -> None:
        for column_name, definition_sql in self.USER_COLUMN_MIGRATIONS:
            self.add_user_column(column_name, definition_sql)

    def _get_user_columns(self) -> set[str]:
        with self._lock:
            rows = self._connection.execute("PRAGMA table_info(users)").fetchall()

        return {row["name"] for row in rows}

    def add_user_column(self, column_name: str, definition_sql: str) -> bool:
        if not self._COLUMN_NAME_RE.match(column_name):
            raise ValueError(f"Invalid column name: {column_name}")

        if len(definition_sql.strip()) == 0:
            raise ValueError("definition_sql cannot be empty")

        if column_name in self._get_user_columns():
            return False

        with self._lock:
            self._connection.execute(
                f"ALTER TABLE users ADD COLUMN {column_name} {definition_sql}"
            )
            self._connection.commit()

        return True

    def ensure_user(self, user_id: int) -> None:
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO users (user_id)
                VALUES (?)
                ON CONFLICT(user_id) DO NOTHING
                """,
                (user_id,),
            )
            self._connection.commit()

    def get_user(self, user_id: int) -> UserRecord | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT user_id, social_score, metadata_json, created_at, updated_at, is_supreme_leader
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        return UserRecord(
            user_id=row["user_id"],
            social_score=row["social_score"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            is_supreme_leader=bool(row["is_supreme_leader"]),
        )

    def get_or_create_user(self, user_id: int) -> UserRecord:
        self.ensure_user(user_id)
        user = self.get_user(user_id)

        if user is None:
            raise RuntimeError(f"Failed to create user record for {user_id}")

        return user

    def set_social_score(self, user_id: int, score: int) -> None:
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO users (user_id, social_score)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET social_score = excluded.social_score
                """,
                (user_id, score),
            )
            self._connection.commit()

    def increment_social_score(self, user_id: int, delta: int = 1) -> int:
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO users (user_id, social_score)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE
                SET social_score = users.social_score + excluded.social_score
                """,
                (user_id, delta),
            )
            self._connection.commit()

        updated_user = self.get_user(user_id)

        if updated_user is None:
            raise RuntimeError(f"Failed to update score for {user_id}")

        return updated_user.social_score

    def set_metadata(self, user_id: int, data: dict[str, Any]) -> None:
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO users (user_id, metadata_json)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET metadata_json = excluded.metadata_json
                """,
                (user_id, json.dumps(data, separators=(",", ":"))),
            )
            self._connection.commit()

    def update_metadata(self, user_id: int, updates: dict[str, Any]) -> dict[str, Any]:
        current = self.get_or_create_user(user_id).metadata
        current.update(updates)
        self.set_metadata(user_id, current)
        return current

    def get_top_users_by_field(self, field_name: str, limit: int = 10) -> list[UserRecord]:
        if field_name not in self._get_user_columns():
            raise ValueError(f"Unknown field: {field_name}")

        with self._lock:
            rows = self._connection.execute(
                f"""
                SELECT user_id, social_score, metadata_json, created_at, updated_at, is_supreme_leader
                FROM users
                ORDER BY {field_name} DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            UserRecord(
                user_id=row["user_id"],
                social_score=row["social_score"],
                metadata=json.loads(row["metadata_json"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                is_supreme_leader=bool(row["is_supreme_leader"]),
            )

            for row in rows
        ]

    def get_metadata(self, user_id: int) -> dict[str, Any]:
        user = self.get_user(user_id)

        if user is None:
            return {}

        return user.metadata

    def get_user_field(self, user_id: int, field_name: str) -> Any | None:
        if field_name not in self._get_user_columns():
            raise ValueError(f"Unknown field: {field_name}")

        with self._lock:
            row = self._connection.execute(
                f"SELECT {field_name} FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        return row[field_name]

    def set_user_field(self, user_id: int, field_name: str, value: Any) -> None:
        if field_name == "user_id":
            raise ValueError("user_id cannot be updated")

        if field_name not in self._get_user_columns():
            raise ValueError(f"Unknown field: {field_name}")

        self.ensure_user(user_id)

        with self._lock:
            self._connection.execute(
                f"UPDATE users SET {field_name} = ? WHERE user_id = ?",
                (value, user_id),
            )
            self._connection.commit()

db = UserDatabase()
