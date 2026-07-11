import sqlite3
from pathlib import Path
from typing import Any

from app.services.admin_knowledge_service import add_admin_article


BACKEND_DIR = Path(__file__).resolve().parents[2]
DRAFT_DB_PATH = BACKEND_DIR / "data" / "knowledge.db"


def connect_db() -> sqlite3.Connection:
    DRAFT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DRAFT_DB_PATH)


def ensure_draft_columns(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(draft_knowledge)")
    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    required_columns = {
        "suggested_answer": "TEXT NOT NULL DEFAULT ''",
        "evidence": "TEXT NOT NULL DEFAULT ''",
        "editorial_warnings": "TEXT NOT NULL DEFAULT ''",
        "category": "TEXT NOT NULL DEFAULT 'general'",
        "draft_type": "TEXT NOT NULL DEFAULT 'runtime_fallback'",
    }

    for column_name, column_definition in required_columns.items():
        if column_name not in existing_columns:
            cursor.execute(
                f"""
                ALTER TABLE draft_knowledge
                ADD COLUMN {column_name} {column_definition}
                """
            )

    connection.commit()


def create_draft_table() -> None:
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS draft_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            suggested_answer TEXT NOT NULL DEFAULT '',
            evidence TEXT NOT NULL DEFAULT '',
            editorial_warnings TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'general',
            draft_type TEXT NOT NULL DEFAULT 'runtime_fallback',
            source TEXT NOT NULL DEFAULT 'internet',
            status TEXT NOT NULL DEFAULT 'draft',
            hit_count INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    ensure_draft_columns(connection)
    connection.close()

def save_draft_answer(
    question: str,
    answer: str,
    *,
    suggested_answer: str = "",
    evidence: str = "",
    editorial_warnings: str = "",
    category: str = "general",
    draft_type: str = "runtime_fallback",
) -> dict[str, Any]:
    create_draft_table()

    clean_question = question.strip()
    clean_answer = answer.strip()
    clean_suggested_answer = suggested_answer.strip()
    clean_evidence = evidence.strip()
    clean_editorial_warnings = editorial_warnings.strip()
    clean_category = category.strip() or "general"
    clean_draft_type = draft_type.strip() or "runtime_fallback"

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, hit_count
        FROM draft_knowledge
        WHERE question = ?
          AND status = 'draft'
        """,
        (clean_question,),
    )

    existing = cursor.fetchone()

    if existing:
        draft_id, hit_count = existing

        cursor.execute(
            """
            UPDATE draft_knowledge
            SET
                answer = ?,
                suggested_answer = ?,
                evidence = ?,
                editorial_warnings = ?,
                category = ?,
                draft_type = ?,
                hit_count = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                clean_answer,
                clean_suggested_answer,
                clean_evidence,
                clean_editorial_warnings,
                clean_category,
                clean_draft_type,
                hit_count + 1,
                draft_id,
            ),
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
            answer,
            suggested_answer,
            evidence,
            editorial_warnings,
            category,
            draft_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            clean_question,
            clean_answer,
            clean_suggested_answer,
            clean_evidence,
            clean_editorial_warnings,
            clean_category,
            clean_draft_type,
        ),
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
        SELECT
            id,
            question,
            answer,
            suggested_answer,
            evidence,
            editorial_warnings,
            category,
            draft_type,
            source,
            status,
            hit_count,
            created_at,
            updated_at
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
            "suggested_answer": row[3],
            "evidence": row[4],
            "editorial_warnings": row[5],
            "category": row[6],
            "draft_type": row[7],
            "source": row[8],
            "status": row[9],
            "hit_count": row[10],
            "created_at": row[11],
            "updated_at": row[12],
        }
        for row in rows
    ]


def get_draft_answer(draft_id: int) -> dict[str, Any]:
    create_draft_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question,
            answer,
            suggested_answer,
            evidence,
            editorial_warnings,
            category,
            draft_type,
            source,
            status,
            hit_count,
            created_at,
            updated_at
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
        "suggested_answer": row[3],
        "evidence": row[4],
        "editorial_warnings": row[5],
        "category": row[6],
        "draft_type": row[7],
        "source": row[8],
        "draft_status": row[9],
        "hit_count": row[10],
        "created_at": row[11],
        "updated_at": row[12],
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

def update_draft_status(
    draft_id: int,
    status: str,
) -> dict[str, Any]:
    create_draft_table()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE draft_knowledge
        SET
            status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (status, draft_id),
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
        "draft_status": status,
    }


def create_article_from_draft(
    draft_id: int,
    approved_question: str,
    approved_answer: str,
    category: str,
) -> dict[str, Any]:
    create_draft_table()

    draft = get_draft_answer(draft_id)

    if draft.get("status") != "found":
        return {
            "status": "not_found",
            "draft_id": draft_id,
        }

    if draft.get("draft_status") != "publishing":
        return {
            "status": "invalid_status",
            "draft_id": draft_id,
            "draft_status": draft.get("draft_status"),
        }

    article_result = add_admin_article(
        question=approved_question,
        answer=approved_answer,
        category=category,
        source="human_reviewed_draft",
        language="kn",
    )

    return {
        "status": "article_created",
        "draft_id": draft_id,
        "question": approved_question,
        "category": category,
        "article": article_result.get("article"),
    }