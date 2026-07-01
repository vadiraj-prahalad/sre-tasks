import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "db" / "knowledge.db"


def load_all_facts() -> dict:
    connection = sqlite3.connect(DB_PATH)
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
        facts[canonical_question] = answer

    return facts
def add_knowledge_item(item: dict) -> None:
    connection = sqlite3.connect(DB_PATH)
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
