import sqlite3
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
DRAFT_DB_PATH = BACKEND_DIR / "data" / "knowledge.db"


def connect_db() -> sqlite3.Connection:
    DRAFT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DRAFT_DB_PATH)


def create_draft_table() -> None:
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS draft_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'ollama_fallback',
            status TEXT NOT NULL DEFAULT 'draft',
            hit_count INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_draft_answer(question: str, answer: str) -> dict[str, Any]:
    create_draft_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, hit_count
        FROM draft_knowledge
        WHERE question = ?
          AND status = 'draft'
        """,
        (question,),
    )

    existing = cursor.fetchone()

    if existing:
        draft_id, hit_count = existing

        cursor.execute(
            """
            UPDATE draft_knowledge
            SET
                answer = ?,
                hit_count = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (answer, hit_count + 1, draft_id),
        )

        connection.commit()
        connection.close()

        return {
            "status": "updated",
            "draft_id": draft_id,
            "hit_count": hit_count + 1,
        }

    cursor.execute(
        """
        INSERT INTO draft_knowledge (
            question,
            answer
        )
        VALUES (?, ?)
        """,
        (question, answer),
    )

    draft_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "status": "created",
        "draft_id": draft_id,
        "hit_count": 1,
    }


def list_draft_answers() -> list[dict[str, Any]]:
    create_draft_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, question, answer, source, status, hit_count, created_at, updated_at
        FROM draft_knowledge
        ORDER BY updated_at DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "source": row[3],
            "status": row[4],
            "hit_count": row[5],
            "created_at": row[6],
            "updated_at": row[7],
        }
        for row in rows
    ]
