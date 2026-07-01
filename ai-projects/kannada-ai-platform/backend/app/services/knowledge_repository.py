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
