import sqlite3
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[3]

STANDARDIZED_DB_PATH = BACKEND_DIR / "data" / "knowledge.db"
APP_DB_PATH = BACKEND_DIR / "app" / "db" / "knowledge.db"

SOURCE_NAME = "standardized_knowledge"


def fetch_standardized_articles() -> list[dict]:
    connection = sqlite3.connect(STANDARDIZED_DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, question, answer, category, source, language
        FROM knowledge_articles
        ORDER BY category, question
        """
    )

    rows = cursor.fetchall()
    connection.close()

    articles = []

    for row in rows:
        articles.append(
            {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "category": row[3],
                "source": row[4],
                "language": row[5],
            }
        )

    return articles


def delete_existing_standardized_documents(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM documents
        WHERE source_name = ?
        """,
        (SOURCE_NAME,),
    )

    document_ids = [row[0] for row in cursor.fetchall()]

    if not document_ids:
        return

    cursor.executemany(
        """
        DELETE FROM chunks
        WHERE document_id = ?
        """,
        [(document_id,) for document_id in document_ids],
    )

    cursor.executemany(
        """
        DELETE FROM documents
        WHERE id = ?
        """,
        [(document_id,) for document_id in document_ids],
    )


def insert_article_as_document(
    connection: sqlite3.Connection,
    article: dict,
) -> None:
    cursor = connection.cursor()

    title = article["question"]
    chunk_text = f"{article['question']}\n\n{article['answer']}"

    cursor.execute(
        """
        INSERT INTO documents (
            title,
            source_name,
            source_url,
            category,
            language,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            SOURCE_NAME,
            article["source"],
            article["category"],
            article["language"],
            "active",
        ),
    )

    document_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO chunks (
            document_id,
            chunk_text,
            chunk_index,
            embedding
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            document_id,
            chunk_text,
            0,
            None,
        ),
    )


def sync_standardized_articles() -> dict:
    articles = fetch_standardized_articles()

    connection = sqlite3.connect(APP_DB_PATH)

    try:
        with connection:
            delete_existing_standardized_documents(connection)

            for article in articles:
                insert_article_as_document(connection, article)

        return {
            "status": "success",
            "articles_synced": len(articles),
            "source_name": SOURCE_NAME,
        }

    finally:
        connection.close()


if __name__ == "__main__":
    result = sync_standardized_articles()

    print("Standardized articles synced")
    print(f"Articles synced: {result['articles_synced']}")
    print(f"Source name: {result['source_name']}")
