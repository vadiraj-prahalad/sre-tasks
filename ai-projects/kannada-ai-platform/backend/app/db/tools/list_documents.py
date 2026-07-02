import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


def main():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        d.id,
        d.title,
        d.category,
        d.language,
        d.source_name,
        COUNT(c.id) AS chunk_count,
        SUM(
            CASE
                WHEN c.embedding IS NOT NULL THEN 1
                ELSE 0
            END
        ) AS embedded_chunks
    FROM documents d
    LEFT JOIN chunks c
        ON d.id = c.document_id
    GROUP BY
        d.id,
        d.title,
        d.category,
        d.language,
        d.source_name
    ORDER BY d.id;
    """)

    rows = cursor.fetchall()

    print("\nKnowledge Library")
    print("=" * 70)

    for row in rows:
        document_id, title, category, language, source_name, chunk_count, embedded_chunks = row

        print(f"\nDocument ID : {document_id}")
        print(f"Title       : {title}")
        print(f"Category    : {category}")
        print(f"Language    : {language}")
        print(f"Source      : {source_name}")
        print(f"Chunks      : {chunk_count}")

        status = "YES" if embedded_chunks == chunk_count else "NO"
        print(f"Embeddings  : {status}")
        print("-" * 70)

    print(f"\nTotal Documents : {len(rows)}")

    connection.close()


if __name__ == "__main__":
    main()
