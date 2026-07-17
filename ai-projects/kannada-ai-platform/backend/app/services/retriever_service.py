import json
import math
import re
import sqlite3
from pathlib import Path

from app.models.knowledge_entity import (
    KnowledgeEntity,
)
from app.services.embedding_service import (
    get_embedding,
)


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "db"
    / "knowledge.db"
)

GENERIC_QUERY_WORDS = {
    "ಯಾರು",
    "ಏನು",
    "ಎಂದರೇನು",
    "ಬಗ್ಗೆ",
    "ಹೇಳಿ",
    "ಜೊತೆ",
    "ಮತ್ತು",
    "ಯಾವುದು",
    "ಹೇಗೆ",
    "ಏಕೆ",
}


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two embedding vectors.
    """

    dot_product = sum(
        value_a * value_b
        for value_a, value_b
        in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(
            value * value
            for value in vector_a
        )
    )

    magnitude_b = math.sqrt(
        sum(
            value * value
            for value in vector_b
        )
    )

    if (
        magnitude_a == 0
        or magnitude_b == 0
    ):
        return 0.0

    return (
        dot_product
        / (magnitude_a * magnitude_b)
    )


def _normalize_terms(
    text: str,
) -> list[str]:
    """
    Extract meaningful lowercase terms for lexical matching.

    Generic Kannada question words describe question structure rather
    than the requested entity, so they must not influence ranking.
    """

    normalized_text = re.sub(
        r"[^\w\u0C80-\u0CFF]+",
        " ",
        (text or "").lower(),
    )

    terms: list[str] = []

    for raw_word in normalized_text.split():
        word = raw_word.strip()

        if len(word) < 3:
            continue

        if word in GENERIC_QUERY_WORDS:
            continue

        terms.append(
            word
        )

    return terms


def keyword_bonus(
    search_text: str,
    target_text: str,
) -> float:
    """
    Reward meaningful lexical overlap.

    Every meaningful query term found in the target receives a small,
    controlled bonus. Generic question words are ignored.

    The bonus is capped so lexical matching supports semantic retrieval
    without overwhelming the embedding score.
    """

    keywords = _normalize_terms(
        search_text
    )

    target_lower = (
        target_text or ""
    ).lower()

    matched_keywords = sum(
        1
        for keyword in keywords
        if keyword in target_lower
    )

    return min(
        matched_keywords * 0.08,
        0.24,
    )


def entity_title_bonus(
    entity: KnowledgeEntity | None,
    title: str,
) -> float:
    """
    Reward document-title overlap with a trusted entity identity.

    Only high-confidence curated alias resolutions are eligible.
    Multiple canonical names, aliases, and trusted query surface forms
    may represent the same entity, so the strongest individual match is
    used rather than accumulating bonuses.
    """

    if entity is None:
        return 0.0

    if (
        entity.resolution_method
        != "alias_lookup"
    ):
        return 0.0

    if entity.confidence < 0.90:
        return 0.0

    candidate_names = [
        entity.resolved_topic,
        entity.canonical_name_en,
        entity.canonical_name_kn,
        entity.display_name,
        entity.normalized_query,
        entity.original_query,
        *entity.aliases_en,
        *entity.aliases_kn,
    ]

    bonuses = [
        keyword_bonus(
            search_text=name,
            target_text=title,
        )
        for name in candidate_names
        if name and name.strip()
    ]

    return max(
        bonuses,
        default=0.0,
    )

def retrieve_chunks(
    question: str,
    limit: int = 3,
    *,
    entity: KnowledgeEntity | None = None,
    evaluation_mode: bool = False,
) -> list[dict]:
    """
    Retrieve the highest-ranking knowledge chunks.

    Ranking combines:

    1. Semantic embedding similarity.
    2. Meaningful lexical overlap with chunk content.
    3. Meaningful lexical overlap with the document title.
    4. Canonical entity overlap with the document title.

    Raw scores are used for ranking so score differences are preserved.

    Bounded scores are exposed to confidence and API consumers so
    operational thresholds remain interpretable.

    High-confidence alias-resolved entities contribute a controlled
    canonical-title overlap signal.

    Entity resolution is intentionally not performed inside this
    service. The router resolves the entity once and passes it
    downstream.
    """

    question_embedding = get_embedding(
        question
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                chunks.chunk_text,
                chunks.embedding,
                documents.title,
                documents.source_name,
                documents.source_url
            FROM chunks
            JOIN documents
                ON chunks.document_id = documents.id
            WHERE chunks.embedding IS NOT NULL
              AND documents.status = 'active'
            """
        )

        rows = cursor.fetchall()

    finally:
        connection.close()

    scored_chunks: list[dict] = []

    for row in rows:
        chunk_text = (
            row[0] or ""
        )

        chunk_embedding = json.loads(
            row[1]
        )

        title = (
            row[2] or ""
        )

        semantic_score = cosine_similarity(
            question_embedding,
            chunk_embedding,
        )

        content_bonus = keyword_bonus(
            search_text=question,
            target_text=chunk_text,
        )

        title_bonus = keyword_bonus(
            search_text=question,
            target_text=title,
        )

        canonical_title_bonus = (
            entity_title_bonus(
                entity=entity,
                title=title,
            )
        )

        raw_score = (
            semantic_score
            + content_bonus
            + title_bonus
            + canonical_title_bonus
        )

        bounded_score = min(
            max(
                raw_score,
                0.0,
            ),
            1.0,
        )

        scored_chunks.append(
            {
                "chunk_text": chunk_text,
                "score": bounded_score,
                "raw_score": raw_score,
                "semantic_score": (
                    semantic_score
                ),
                "keyword_bonus": (
                    content_bonus
                ),
                "title_bonus": (
                    title_bonus
                ),
                "entity_title_bonus": (
                    canonical_title_bonus
                ),
                "title": title,
                "source_name": row[3],
                "source_url": row[4],
            }
        )

    scored_chunks.sort(
        key=lambda item: (
            item["raw_score"],
            item["entity_title_bonus"],
            item["title_bonus"],
            item["keyword_bonus"],
            item["semantic_score"],
        ),
        reverse=True,
    )

    if not scored_chunks:
        return []

    if evaluation_mode:
        return scored_chunks[:limit]

    top_raw_score = (
        scored_chunks[0][
            "raw_score"
        ]
    )

    second_raw_score = (
        scored_chunks[1][
            "raw_score"
        ]
        if len(scored_chunks) > 1
        else 0.0
    )

    score_gap = (
        top_raw_score
        - second_raw_score
    )

    if (
        top_raw_score >= 0.85
        or score_gap >= 0.05
    ):
        return scored_chunks[:1]

    return scored_chunks[:limit]