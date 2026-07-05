import sqlite3
from pathlib import Path


APP_DB_PATH = Path(__file__).resolve().parent.parent / "db" / "knowledge.db"
STANDARDIZED_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge.db"


def load_standardized_articles() -> dict:
    if not STANDARDIZED_DB_PATH.exists():
        return {}

    connection = sqlite3.connect(STANDARDIZED_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT question, answer
        FROM knowledge_articles
        """
    )

    rows = cursor.fetchall()
    connection.close()

    facts = {}

    for question, answer in rows:
        facts[question.strip().lower()] = answer

    return facts


def load_curated_facts() -> dict:
    connection = sqlite3.connect(APP_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT canonical_question, answer
        FROM knowledge_items
        """
    )

    rows = cursor.fetchall()
    connection.close()

    facts = {}

    for canonical_question, answer in rows:
        facts[canonical_question.strip().lower()] = answer

    return facts


def load_all_facts() -> dict:
    facts = load_curated_facts()
    facts.update(load_standardized_articles())
    return facts


def add_knowledge_item(item: dict) -> None:
    connection = sqlite3.connect(APP_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO knowledge_items (
            canonical_question,
            answer,
            category,
            language,
            source,
            confidence,
            item_type,
            canonical_key,
            title,
            domain,
            subdomain,
            keywords,
            related_topics,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item["canonical_question"],
            item["answer"],
            item["category"],
            item.get("language", "kn"),
            item.get("source", "curated"),
            item.get("confidence", "verified"),
            item.get("item_type", "entity"),
            item["canonical_key"],
            item["title"],
            item["domain"],
            item.get("subdomain"),
            item.get("keywords"),
            item.get("related_topics"),
            item.get("status", "published"),
        ),
    )
    connection.commit()
    connection.close()


def update_answer(canonical_key: str, answer: str) -> None:
    connection = sqlite3.connect(APP_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE knowledge_items
        SET
            answer = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE canonical_key = ?
        """,
        (answer, canonical_key),
    )

    connection.commit()
    connection.close()


def delete_knowledge_item(canonical_key: str) -> None:
    connection = sqlite3.connect(APP_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM knowledge_items
        WHERE canonical_key = ?
        """,
        (canonical_key,),
    )

    connection.commit()
    connection.close()


def search_knowledge_items(search_text: str) -> list[dict]:
    connection = sqlite3.connect(APP_DB_PATH)
    cursor = connection.cursor()

    like_pattern = f"%{search_text}%"

    cursor.execute(
        """
        SELECT canonical_key, title, canonical_question, answer, domain, subdomain
        FROM knowledge_items
        WHERE
            canonical_question LIKE ?
            OR answer LIKE ?
            OR title LIKE ?
            OR domain LIKE ?
            OR subdomain LIKE ?
            OR keywords LIKE ?
        ORDER BY id
        """,
        (
            like_pattern,
            like_pattern,
            like_pattern,
            like_pattern,
            like_pattern,
            like_pattern,
        ),
    )

    rows = cursor.fetchall()
    connection.close()

    results = []

    for row in rows:
        results.append(
            {
                "canonical_key": row[0],
                "title": row[1],
                "canonical_question": row[2],
                "answer": row[3],
                "domain": row[4],
                "subdomain": row[5],
            }
        )

    return results


def find_answer_by_key(canonical_key: str) -> str | None:
    connection = sqlite3.connect(APP_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT answer
        FROM knowledge_items
        WHERE canonical_key = ?
          AND status = 'published'
        """,
        (canonical_key,),
    )

    row = cursor.fetchone()
    connection.close()

    if row:
        return row[0]

    return None