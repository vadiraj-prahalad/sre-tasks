import json
import math
import sqlite3
from pathlib import Path

from app.llm.local_llm import get_llm_response
from app.services.answer_strategy import should_use_direct_answer
from app.services.embedding_service import get_embedding
from backend.app.db.tools.semantic_search_chunks import keyword_bonus


DB_PATH = Path(__file__).resolve().parent.parent / "db" / "knowledge.db"
MIN_SIMILARITY_SCORE = 0.70


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def semantic_search_chunks(question: str, limit: int = 3) -> list[dict]:
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
        score = semantic_score + bonus
        scored_chunks.append(
            {
                "chunk_text": chunk_text,
                "score": score,
                "semantic_score": semantic_score,
                "keyword_bonus": bonus,
                "title": row[2],
                "source_name": row[3],
                "source_url": row[4],
            }
        )

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    return scored_chunks[:limit]


def build_sources_text(chunks: list[dict]) -> str:
    source_titles = []

    for chunk in chunks:
        title = chunk["title"]
        if title not in source_titles:
            source_titles.append(title)

    return "\n".join([f"ಮೂಲ: {title}" for title in source_titles])


def build_prompt(context: str, question: str) -> str:
    return f"""
ನೀವು ವಿಶ್ವಾಸಾರ್ಹ ಕನ್ನಡ ಜ್ಞಾನ ಸಹಾಯಕರು.

ಕಟ್ಟುನಿಟ್ಟಿನ ನಿಯಮಗಳು:
1. ಕೆಳಗಿನ ಮೂಲ ಮಾಹಿತಿಯನ್ನು ಮಾತ್ರ ಬಳಸಿ ಉತ್ತರಿಸಿ.
2. ಮೂಲ ಮಾಹಿತಿಯಲ್ಲಿ ಇಲ್ಲದ ವಿಷಯವನ್ನು ಸೇರಿಸಬೇಡಿ.
3. ಮೂಲದಲ್ಲಿರುವ ತತ್ತ್ವ, ಹೆಸರು, ಸಂಬಂಧ, ಅರ್ಥಗಳನ್ನು ಬದಲಾಯಿಸಬೇಡಿ.
4. "ಭೇದವಿದೆ" ಎಂದಿದ್ದರೆ ಅದನ್ನು "ಭೇದವಿಲ್ಲ" ಎಂದು ಬದಲಾಯಿಸಬೇಡಿ.
5. ಉತ್ತರ ಚಿಕ್ಕದಾಗಿ, ಸ್ಪಷ್ಟವಾಗಿ ಮತ್ತು ಸರಳ ಕನ್ನಡದಲ್ಲಿ ಇರಲಿ.
6. ಖಚಿತ ಮಾಹಿತಿ ಇಲ್ಲದಿದ್ದರೆ: "ಮೂಲ ಮಾಹಿತಿಯಲ್ಲಿ ಇದಕ್ಕೆ ಸ್ಪಷ್ಟ ಉತ್ತರ ಇಲ್ಲ." ಎಂದು ಹೇಳಿ.

ಮೂಲ ಮಾಹಿತಿ:
{context}

ಪ್ರಶ್ನೆ:
{question}

ಉತ್ತರ:
"""


def answer_from_rag(question: str) -> str | None:
    chunks = semantic_search_chunks(question)

    if not chunks:
        return None

    best_score = chunks[0]["score"]

    if best_score < MIN_SIMILARITY_SCORE:
        return None

    sources_text = build_sources_text(chunks)

    if should_use_direct_answer(question):
        direct_answer = chunks[0]["chunk_text"]
        return f"{direct_answer}\n\n{sources_text}"

    context = "\n\n".join([chunk["chunk_text"] for chunk in chunks])
    prompt = build_prompt(context, question)

    answer = get_llm_response(prompt)

    return f"{answer}\n\n{sources_text}"

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