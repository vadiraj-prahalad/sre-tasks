import json
import math
import sqlite3
from pathlib import Path

from app.services.embedding_service import get_embedding


DB_PATH = Path(__file__).resolve().parent.parent / "db" / "knowledge.db"


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


def retrieve_chunks(question: str, limit: int = 3) -> list[dict]:
    question_embedding = get_embedding(question)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
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

    scored_chunks = []

    for row in rows:
        chunk_text = row[0]
        chunk_embedding = json.loads(row[1])

        semantic_score = cosine_similarity(question_embedding, chunk_embedding)
        bonus = keyword_bonus(question, chunk_text)
        final_score = semantic_score + bonus

        scored_chunks.append(
            {
                "chunk_text": chunk_text,
                "score": final_score,
                "semantic_score": semantic_score,
                "keyword_bonus": bonus,
                "title": row[2],
                "source_name": row[3],
                "source_url": row[4],
            }
        )

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    if not scored_chunks:
        return []

    top_score = scored_chunks[0]["score"]

    second_score = scored_chunks[1]["score"] if len(scored_chunks) > 1 else 0
    score_gap = top_score - second_score

    if top_score >= 0.85 or score_gap >= 0.05:
        return scored_chunks[:1]

    return scored_chunks[:limit]
