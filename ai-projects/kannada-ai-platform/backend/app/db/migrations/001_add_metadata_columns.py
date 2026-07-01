import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


COLUMNS_TO_ADD = [
    ("item_type", "TEXT DEFAULT 'qa'"),
    ("canonical_key", "TEXT"),
    ("title", "TEXT"),
    ("domain", "TEXT"),
    ("subdomain", "TEXT"),
    ("keywords", "TEXT"),
    ("related_topics", "TEXT"),
    ("status", "TEXT DEFAULT 'published'"),
]


def column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)


def migrate() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    for column_name, column_type in COLUMNS_TO_ADD:
        if not column_exists(cursor, "knowledge_items", column_name):
            cursor.execute(
                f"ALTER TABLE knowledge_items ADD COLUMN {column_name} {column_type}"
            )
            print(f"Added column: {column_name}")
        else:
            print(f"Column already exists: {column_name}")

    connection.commit()
    connection.close()

    print("Migration completed successfully.")


if __name__ == "__main__":
    migrate()
