import sqlite3
from pathlib import Path
from typing import Any

from app.services.admin_knowledge_service import add_admin_article


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


def get_draft_answer(draft_id: int) -> dict[str, Any]:
    create_draft_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, question, answer, source, status, hit_count, created_at, updated_at
        FROM draft_knowledge
        WHERE id = ?
        """,
        (draft_id,),
    )

    row = cursor.fetchone()
    connection.close()

    if not row:
        return {
            "status": "not_found",
            "draft_id": draft_id,
        }

    return {
        "status": "found",
        "id": row[0],
        "question": row[1],
        "answer": row[2],
        "source": row[3],
        "draft_status": row[4],
        "hit_count": row[5],
        "created_at": row[6],
        "updated_at": row[7],
    }


def update_draft_answer(
    draft_id: int,
    question: str,
    answer: str,
) -> dict[str, Any]:
    create_draft_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE draft_knowledge
        SET
            question = ?,
            answer = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (question, answer, draft_id),
    )

    updated_count = cursor.rowcount

    connection.commit()
    connection.close()

    if updated_count == 0:
        return {
            "status": "not_found",
            "draft_id": draft_id,
        }

    return {
        "status": "updated",
        "draft_id": draft_id,
    }


def delete_draft_answer(draft_id: int) -> dict[str, Any]:
    create_draft_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM draft_knowledge
        WHERE id = ?
        """,
        (draft_id,),
    )

    existing = cursor.fetchone()

    if not existing:
        connection.close()
        return {
            "status": "not_found",
            "draft_id": draft_id,
        }

    cursor.execute(
        """
        DELETE FROM draft_knowledge
        WHERE id = ?
        """,
        (draft_id,),
    )

    connection.commit()
    connection.close()

    return {
        "status": "deleted",
        "draft_id": draft_id,
    }


def approve_draft_answer(
    draft_id: int,
    approved_question: str,
    approved_answer: str,
    category: str,
) -> dict[str, Any]:
    create_draft_table()

    draft = get_draft_answer(draft_id)

    if draft.get("status") != "found" or draft.get("draft_status") != "draft":
        return {
            "status": "not_found",
            "draft_id": draft_id,
        }

    article_result = add_admin_article(
        question=approved_question,
        answer=approved_answer,
        category=category,
        source="human_reviewed_draft",
        language="kn",
    )

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE draft_knowledge
        SET
            status = 'approved',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (draft_id,),
    )

    connection.commit()
    connection.close()

    return {
        "status": "approved",
        "draft_id": draft_id,
        "question": approved_question,
        "category": category,
        "article": article_result.get("article"),
    }