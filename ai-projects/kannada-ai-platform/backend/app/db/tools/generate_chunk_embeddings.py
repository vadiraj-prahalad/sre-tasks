import json
import sqlite3
from pathlib import Path

from app.services.embedding_service import get_embedding


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


def generate_chunk_embeddings() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, chunk_text
        FROM chunks
        WHERE embedding IS NULL
        """
    )

    rows = cursor.fetchall()

    if not rows:
        print("No chunks without embeddings found.")
        connection.close()
        return

    for chunk_id, chunk_text in rows:
        embedding = get_embedding(chunk_text)

        cursor.execute(
            """
            UPDATE chunks
            SET embedding = ?
            WHERE id = ?
            """,
            (json.dumps(embedding), chunk_id),
        )

        print(f"Generated embedding for chunk ID: {chunk_id}")

    connection.commit()
    connection.close()

    print("Chunk embedding generation completed.")


if __name__ == "__main__":
    generate_chunk_embeddings()
