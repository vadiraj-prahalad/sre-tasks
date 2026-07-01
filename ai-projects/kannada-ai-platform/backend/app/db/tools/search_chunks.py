import sqlite3
import sys
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


def search_chunks(search_text: str) -> list[dict]:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    like_pattern = f"%{search_text}%"

    cursor.execute(
        """
        SELECT
            chunks.id,
            documents.title,
            documents.source_name,
            documents.category,
            chunks.chunk_text
        FROM chunks
        JOIN documents ON chunks.document_id = documents.id
        WHERE chunks.chunk_text LIKE ?
        ORDER BY chunks.id
        """,
        (like_pattern,),
    )

    rows = cursor.fetchall()
    connection.close()

    results = []

    for row in rows:
        results.append(
            {
                "chunk_id": row[0],
                "title": row[1],
                "source_name": row[2],
                "category": row[3],
                "chunk_text": row[4],
            }
        )

    return results


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python app/db/tools/search_chunks.py <search_text>")
        return

    search_text = sys.argv[1]
    results = search_chunks(search_text)

    if not results:
        print("No matching chunks found.")
        return

    print("\nMatching RAG Chunks\n")
    print("-" * 80)

    for item in results:
        print(f"Chunk ID: {item['chunk_id']}")
        print(f"Title: {item['title']}")
        print(f"Source: {item['source_name']}")
        print(f"Category: {item['category']}")
        print(f"Text: {item['chunk_text']}")
        print("-" * 80)


if __name__ == "__main__":
    main()
