import sqlite3
import sys
from pathlib import Path

from app.services.chunking_service import split_into_chunks
from app.services.document_loader import load_document


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


def ingest_text_document(
    file_path: str,
    title: str,
    source_name: str,
    category: str,
    language: str = "kn",
) -> None:
    content = load_document(file_path)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM documents
        WHERE title = ?
          AND source_name = ?
        """,
        (title, source_name),
    )

    existing_document = cursor.fetchone()

    if existing_document:
        connection.close()
        print(f"Document already exists, skipping: {title}")
        return

    cursor.execute(
        """
        INSERT INTO documents (
            title,
            source_name,
            source_url,
            category,
            language
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, source_name, None, category, language),
    )

    document_id = cursor.lastrowid
    chunks = split_into_chunks(content)

    for index, chunk_text in enumerate(chunks):
        cursor.execute(
            """
            INSERT INTO chunks (
                document_id,
                chunk_text,
                chunk_index
            )
            VALUES (?, ?, ?)
            """,
            (document_id, chunk_text, index),
        )

    connection.commit()
    connection.close()

    print(f"Inserted document ID: {document_id}")
    print(f"Inserted chunks: {len(chunks)}")


def main() -> None:
    if len(sys.argv) < 5:
        print(
            "Usage: python -m app.db.tools.ingest_text_document "
            "<file_path> <title> <source_name> <category>"
        )
        return

    ingest_text_document(
        file_path=sys.argv[1],
        title=sys.argv[2],
        source_name=sys.argv[3],
        category=sys.argv[4],
    )


if __name__ == "__main__":
    main()