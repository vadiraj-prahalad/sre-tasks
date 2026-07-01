import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


def migrate() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_url TEXT,
            category TEXT,
            language TEXT NOT NULL DEFAULT 'kn',
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            embedding TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
        """
    )

    connection.commit()
    connection.close()

    print("RAG tables created successfully.")


if __name__ == "__main__":
    migrate()
