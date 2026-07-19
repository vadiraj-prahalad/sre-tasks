import json
import math
import sqlite3
from pathlib import Path

from app.models.knowledge_entity import (
    KnowledgeEntity,
)
from app.services.embedding_service import (
    get_embedding,
)

from app.services.text_normalization_service import (
    fold_kannada_for_matching,
    normalize_terms,
    normalize_unicode,
)


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "db"
    / "knowledge.db"
)

def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two embedding vectors.
    """

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(
            vector_a,
            vector_b,
        )
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


def keyword_bonus(
    search_text: str,
    target_text: str,
) -> float:
    """
    Reward meaningful lexical overlap.

    Exact lexical matching is attempted first. Kannada terms also receive
    a conservative orthographic comparison that ignores virama and
    zero-width join-control characters.

    Each meaningful query term contributes at most once. The total bonus
    remains capped so lexical matching cannot overwhelm semantic
    retrieval.
    """

    keywords = normalize_terms(
        search_text
    )

    target_normalized = normalize_unicode(
        target_text
    )

    folded_target = fold_kannada_for_matching(
        target_text
    )

    matched_keywords = 0

    for keyword in keywords:
        if keyword in target_normalized:
            matched_keywords += 1
            continue

        folded_keyword = (
            fold_kannada_for_matching(
                keyword
            )
        )

        if (
            folded_keyword
            and len(folded_keyword) >= 3
            and folded_keyword
            in folded_target
        ):
            matched_keywords += 1

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
    can represent the same entity. The strongest individual match is
    used instead of accumulating bonuses from multiple identity forms.
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
    4. Trusted entity overlap with the document title.

    Raw scores are used for ranking so score differences are preserved.

    Bounded scores are exposed to confidence and API consumers so
    operational thresholds remain interpretable.

    High-confidence alias-resolved entities contribute a controlled
    title-overlap signal.

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
        scored_chunks[0]["raw_score"]
    )

    second_raw_score = (
        scored_chunks[1]["raw_score"]
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