import sqlite3
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BACKEND_DIR / "data" / "knowledge.db"


def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_feedback_table() -> None:
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            rating TEXT NOT NULL,
            confidence_score INTEGER,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_feedback(
    question: str,
    answer: str,
    rating: str,
    confidence_score: int | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    create_feedback_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO feedback (
            question,
            answer,
            rating,
            confidence_score,
            source
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (question, answer, rating, confidence_score, source),
    )

    feedback_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "status": "saved",
        "feedback_id": feedback_id,
    }
