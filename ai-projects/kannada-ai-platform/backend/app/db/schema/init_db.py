import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"

def init_db() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_question TEXT NOT NULL UNIQUE,
            answer TEXT NOT NULL,
            category TEXT NOT NULL,
            language TEXT NOT NULL DEFAULT 'kn',
            source TEXT NOT NULL DEFAULT 'curated',
            confidence TEXT NOT NULL DEFAULT 'verified',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()

    print(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_db()
