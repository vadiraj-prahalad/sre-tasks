import json
import math
import sqlite3
import sys
from pathlib import Path

from app.services.embedding_service import get_embedding


DB_PATH = Path(__file__).resolve().parent.parent / "knowledge.db"


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

def keyword_bonus(search_text: str, chunk_text: str) -> float:
    keywords = [
        word.strip().lower()
        for word in search_text.split()
        if len(word.strip()) >= 3
    ]

    chunk_lower = chunk_text.lower()

    matched_keywords = 0

    for keyword in keywords:
        if keyword in chunk_lower:
            matched_keywords += 1

    return matched_keywords * 0.05

def semantic_search(search_text: str, limit: int = 3) -> list[dict]:
    query_embedding = get_embedding(search_text)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            chunks.id,
            chunks.chunk_text,
            chunks.embedding,
            documents.title,
            documents.source_name,
            documents.source_url
        FROM chunks
        JOIN documents ON chunks.document_id = documents.id
        WHERE chunks.embedding IS NOT NULL
        """
    )

    rows = cursor.fetchall()
    connection.close()

    scored_results = []

    for row in rows:
        chunk_id = row[0]
        chunk_text = row[1]
        chunk_embedding = json.loads(row[2])
        title = row[3]
        source_name = row[4]
        source_url = row[5]

        semantic_score = cosine_similarity(query_embedding, chunk_embedding)
        bonus = keyword_bonus(search_text, chunk_text)
        score = semantic_score + bonus
        scored_results.append(
            {
                "chunk_id": chunk_id,
                "score": score,
                "semantic_score": semantic_score,
                "keyword_bonus": bonus,
                "chunk_text": chunk_text,
                "title": title,
                "source_name": source_name,
                "source_url": source_url,
            }
        )

    scored_results.sort(key=lambda item: item["score"], reverse=True)

    return scored_results[:limit]


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.db.tools.semantic_search_chunks <question>")
        return

    search_text = " ".join(sys.argv[1:])
    results = semantic_search(search_text)

    if not results:
        print("No semantic results found.")
        return

    print("\nSemantic Search Results\n")
    print("-" * 80)

    for item in results:
        print(f"Chunk ID: {item['chunk_id']}")
        print(f"Score: {item['score']:.4f}")
        print(f"Semantic Score: {item['semantic_score']:.4f}")
        print(f"Keyword Bonus: {item['keyword_bonus']:.4f}")
        print(f"Title: {item['title']}")
        print(f"Source: {item['source_name']}")
        preview = item["chunk_text"][:160]
        print(f"Text Preview: {preview}...")
        print("-" * 80)


if __name__ == "__main__":
    main()
