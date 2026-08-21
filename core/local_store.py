"""Persistencia local de MentorAI.

Filosofía: una sola base SQLite por perfil local, sin telemetría, sin cuentas
remotas y con el texto de consultas/respuestas cifrado antes de persistirlo.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.security_manager import SecurityManager


@dataclass(frozen=True)
class Progress:
    points: int
    level: int
    experience: int
    streak: int
    topics_completed: int


@dataclass(frozen=True)
class HistoryItem:
    question: str
    answer: str
    topic: str
    created_at: str


class LocalStore:
    """Repositorio SQLite local con conexiones cortas y transacciones explícitas."""

    USER_ID = "local-user"

    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".mentorai"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "mentorai.db"
        self.security = SecurityManager(data_dir=self.data_dir)
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS profile (
                    user_id TEXT PRIMARY KEY,
                    language TEXT NOT NULL DEFAULT 'es',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS progress (
                    user_id TEXT PRIMARY KEY REFERENCES profile(user_id) ON DELETE CASCADE,
                    points INTEGER NOT NULL DEFAULT 0,
                    level INTEGER NOT NULL DEFAULT 1,
                    experience INTEGER NOT NULL DEFAULT 0,
                    streak INTEGER NOT NULL DEFAULT 0,
                    topics_completed INTEGER NOT NULL DEFAULT 0,
                    completed_topics TEXT NOT NULL DEFAULT '[]'
                );
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL REFERENCES profile(user_id) ON DELETE CASCADE,
                    question_token TEXT NOT NULL,
                    answer_token TEXT NOT NULL,
                    topic TEXT NOT NULL DEFAULT 'General',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_history_user_created
                    ON history(user_id, created_at DESC);
                """)
            now = datetime.now(timezone.utc).isoformat()
            connection.execute(
                "INSERT OR IGNORE INTO profile(user_id, language, created_at, updated_at) VALUES (?, 'es', ?, ?)",
                (self.USER_ID, now, now),
            )
            connection.execute(
                "INSERT OR IGNORE INTO progress(user_id) VALUES (?)",
                (self.USER_ID,),
            )

    def get_language(self) -> str:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT language FROM profile WHERE user_id = ?", (self.USER_ID,)
            ).fetchone()
        return str(row["language"]) if row else "es"

    def set_language(self, language: str) -> None:
        language = language if language in {"es", "en", "pt", "ca"} else "es"
        with self._connect() as connection:
            connection.execute(
                "UPDATE profile SET language = ?, updated_at = ? WHERE user_id = ?",
                (language, datetime.now(timezone.utc).isoformat(), self.USER_ID),
            )

    def get_progress(self) -> Progress:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT points, level, experience, streak, topics_completed FROM progress WHERE user_id = ?",
                (self.USER_ID,),
            ).fetchone()
        if not row:
            return Progress(0, 1, 0, 0, 0)
        return Progress(
            *(
                int(row[column])
                for column in (
                    "points",
                    "level",
                    "experience",
                    "streak",
                    "topics_completed",
                )
            )
        )

    def record_query(
        self, question: str, answer: str, topic: str = "General"
    ) -> Progress:
        """Guarda una interacción cifrada y recompensa una consulta educativa."""
        now = datetime.now(timezone.utc).isoformat()
        question_token = self.security.encrypt_data(question, "history.question")
        answer_token = self.security.encrypt_data(answer, "history.answer")
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO history(user_id, question_token, answer_token, topic, created_at) VALUES (?, ?, ?, ?, ?)",
                (self.USER_ID, question_token, answer_token, topic[:120], now),
            )
            connection.execute(
                "UPDATE progress SET points = points + 10, experience = experience + 10 WHERE user_id = ?",
                (self.USER_ID,),
            )
            self._recalculate_level(connection)
        return self.get_progress()

    def complete_topic(self, topic: str) -> Progress:
        topic = topic.strip()[:120] or "General"
        with self._connect() as connection:
            row = connection.execute(
                "SELECT completed_topics FROM progress WHERE user_id = ?",
                (self.USER_ID,),
            ).fetchone()
            completed = json.loads(row["completed_topics"] if row else "[]")
            if topic not in completed:
                completed.append(topic)
                connection.execute(
                    "UPDATE progress SET points = points + 50, experience = experience + 50, topics_completed = ?, completed_topics = ? WHERE user_id = ?",
                    (
                        len(completed),
                        json.dumps(completed, ensure_ascii=False),
                        self.USER_ID,
                    ),
                )
                self._recalculate_level(connection)
        return self.get_progress()

    @staticmethod
    def _recalculate_level(connection: sqlite3.Connection) -> None:
        row = connection.execute(
            "SELECT points FROM progress WHERE user_id = ?", (LocalStore.USER_ID,)
        ).fetchone()
        points = int(row["points"]) if row else 0
        level = 1
        threshold = 100
        while points >= threshold:
            level += 1
            threshold += 100 * level
        connection.execute(
            "UPDATE progress SET level = ? WHERE user_id = ?",
            (level, LocalStore.USER_ID),
        )

    def get_history(self, limit: int = 25) -> list[HistoryItem]:
        limit = max(1, min(int(limit), 100))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT question_token, answer_token, topic, created_at FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (self.USER_ID, limit),
            ).fetchall()
        history: list[HistoryItem] = []
        for row in rows:
            try:
                question = self.security.decrypt_data(
                    row["question_token"], "history.question"
                )
                answer = self.security.decrypt_data(
                    row["answer_token"], "history.answer"
                )
            except Exception:
                question, answer = (
                    "[No disponible: registro corrupto]",
                    "[No disponible]",
                )
            history.append(
                HistoryItem(question, answer, str(row["topic"]), str(row["created_at"]))
            )
        return history

    def export_privacy_summary(self) -> dict[str, Any]:
        progress = self.get_progress()
        return {
            "database": str(self.db_path),
            "history_records": len(self.get_history(100)),
            "progress": progress.__dict__,
            "security": self.security.generate_privacy_report(),
        }

    def delete_all(self) -> None:
        """Borra el perfil, los registros y la clave local; la UI confirma antes."""
        with self._connect() as connection:
            connection.execute("DELETE FROM profile WHERE user_id = ?", (self.USER_ID,))
        self.security.wipe_all_data(
            [
                self.db_path,
                self.data_dir / "mentorai.db-wal",
                self.data_dir / "mentorai.db-shm",
                self.security.key_path,
            ]
        )

    def reset_profile(self) -> None:
        """Crea una nueva clave y perfil después de una eliminación completa."""
        self.security = SecurityManager(data_dir=self.data_dir)
        self._initialise()


if __name__ == "__main__":
    store = LocalStore(Path.home() / ".mentorai")
    print(store.export_privacy_summary())
