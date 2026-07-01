import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"

def list_items() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, canonical_question, category, confidence
        FROM knowledge_items
        ORDER BY id
        """
    )

    rows = cursor.fetchall()
    connection.close()

    if not rows:
        print("No knowledge items found.")
        return

    print("\nKannada Knowledge Items\n")
    print("-" * 80)

    for item_id, question, category, confidence in rows:
        print(f"ID: {item_id}")
        print(f"Question: {question}")
        print(f"Category: {category}")
        print(f"Confidence: {confidence}")
        print("-" * 80)


if __name__ == "__main__":
    list_items()
