from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalExplanation:
    """
    Deterministic explanation of why a retrieved chunk was selected.

    This model explains ranking signals already produced by the
    retriever. It does not assess truthfulness, alter ranking, or make
    answer-generation decisions.
    """

    selected_title: str
    reasons: tuple[str, ...]
    semantic_score: float
    content_bonus: float
    title_bonus: float
    entity_title_bonus: float
    raw_score: float
    bounded_score: float
    source_name: str
    provenance: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _score(
    selected_chunk: dict[str, Any],
    key: str,
    default: float = 0.0,
) -> float:
    """
    Safely read a numeric retrieval signal.
    """

    try:
        return float(
            selected_chunk.get(
                key,
                default,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        return default


def explain_retrieval(
    selected_chunk: dict[str, Any],
    result_count: int,
) -> RetrievalExplanation:
    """
    Build an evidence-backed explanation for the selected chunk.

    Reasons are derived only from observable retriever signals. The
    function intentionally avoids subjective quality statements such as
    "trustworthy" or "excellent evidence".
    """

    semantic_score = _score(
        selected_chunk,
        "semantic_score",
    )

    content_bonus = _score(
        selected_chunk,
        "keyword_bonus",
    )

    title_bonus = _score(
        selected_chunk,
        "title_bonus",
    )

    entity_title_bonus = _score(
        selected_chunk,
        "entity_title_bonus",
    )

    raw_score = _score(
        selected_chunk,
        "raw_score",
        _score(
            selected_chunk,
            "score",
        ),
    )

    bounded_score = _score(
        selected_chunk,
        "score",
    )

    reasons: list[str] = []

    if entity_title_bonus > 0.0:
        reasons.append(
            "Canonical entity matched the document title."
        )

    if title_bonus > 0.0:
        reasons.append(
            "Question terms matched the document title."
        )

    if content_bonus > 0.0:
        reasons.append(
            "Question terms matched the document content."
        )

    if semantic_score > 0.0:
        reasons.append(
            "Document had semantic similarity with the question."
        )

    if result_count == 1:
        reasons.append(
            "Retriever retained one clear top result."
        )
    elif result_count > 1:
        reasons.append(
            "Retriever retained multiple relevant context chunks."
        )
    else:
        reasons.append(
            "No retrieved result count was available."
        )

    return RetrievalExplanation(
        selected_title=str(
            selected_chunk.get(
                "title",
                "",
            )
        ),
        reasons=tuple(
            reasons
        ),
        semantic_score=semantic_score,
        content_bonus=content_bonus,
        title_bonus=title_bonus,
        entity_title_bonus=entity_title_bonus,
        raw_score=raw_score,
        bounded_score=bounded_score,
        source_name=str(
            selected_chunk.get(
                "source_name",
                "unknown",
            )
        ),
        provenance=str(
            selected_chunk.get(
                "source_url",
            )
            or "not_recorded"
        ),
    )
