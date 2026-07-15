"""
Retrieval Baseline Evaluator
============================

Measures retrieval quality independently of answer generation.

Metrics:
- Hit@1
- Hit@3
- Mean Reciprocal Rank
- Average retrieval latency
- Average semantic score
- Average content bonus
- Average title bonus
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from app.services.retriever_service import (
    retrieve_chunks,
)


@dataclass(frozen=True)
class RetrievalCase:
    question: str
    acceptable_title_terms: tuple[str, ...]


TEST_CASES = [
    RetrievalCase(
        question="ಕುವೆಂಪು ಯಾರು?",
        acceptable_title_terms=(
            "ಕುವೆಂಪು",
        ),
    ),
    RetrievalCase(
        question=(
            "ಕುವೆಂಪು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ನೀಡಿದ ಕೊಡುಗೆ"
        ),
        acceptable_title_terms=(
            "Kuvempu",
            "ಕುವೆಂಪು",
        ),
    ),
    RetrievalCase(
        question="ಪುರಂದರ ದಾಸರು ಯಾರು?",
        acceptable_title_terms=(
            "ಪುರಂದರ ದಾಸರು",
        ),
    ),
    RetrievalCase(
        question="ಪುರಂದರ ದಾಸರ ಕೊಡುಗೆ",
        acceptable_title_terms=(
            "ಪುರಂದರ ದಾಸರ ಕೊಡುಗೆ",
        ),
    ),
    RetrievalCase(
        question="ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?",
        acceptable_title_terms=(
            "ಮಧ್ವಾಚಾರ್ಯರು",
            "Madhwacharya",
        ),
    ),
    RetrievalCase(
        question=(
            "ಉಡುಪಿ ಮಠದ ಜೊತೆ ಮಧ್ವರ ಸಂಬಂಧ ಏನು"
        ),
        acceptable_title_terms=(
            "Madhwacharya",
            "ಮಧ್ವಾಚಾರ್ಯ",
        ),
    ),
    RetrievalCase(
        question="ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?",
        acceptable_title_terms=(
            "ವಿಷ್ಣುವರ್ಧನ್",
            "Vishnuvardhan",
        ),
    ),
    RetrievalCase(
        question="ಡಾ ವಿಷ್ಣುವರ್ಧನ್ ಬಗ್ಗೆ ಹೇಳಿ",
        acceptable_title_terms=(
            "ಡಾ ವಿಷ್ಣುವರ್ಧನ್",
            "ವಿಷ್ಣುವರ್ಧನ್",
            "Dr Vishnuvardhan",
        ),
    ),
    RetrievalCase(
        question="ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?",
        acceptable_title_terms=(
            "Dr Rajkumar",
            "ರಾಜಕುಮಾರ್",
            "ರಾಜ್‌ಕುಮಾರ್",
        ),
    ),
    RetrievalCase(
        question="ಮೈಸೂರು ಅರಮನೆ ಬಗ್ಗೆ ಹೇಳಿ",
        acceptable_title_terms=(
            "ಮೈಸೂರು ಅರಮನೆ",
            "Mysore Palace",
        ),
    ),
]


def _find_rank(
    results: list[dict],
    acceptable_title_terms: tuple[str, ...],
) -> int | None:
    normalized_terms = tuple(
        term.casefold()
        for term in acceptable_title_terms
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):
        title = str(
            result.get("title") or ""
        ).casefold()

        if any(
            term in title
            for term in normalized_terms
        ):
            return rank

    return None


def evaluate() -> dict:
    hit_at_1 = 0
    hit_at_3 = 0
    reciprocal_rank_total = 0.0

    latency_total_ms = 0.0
    semantic_total = 0.0
    content_bonus_total = 0.0
    title_bonus_total = 0.0

    scored_result_count = 0
    failures: list[dict] = []

    print("=" * 88)
    print("Retrieval Baseline Evaluation")
    print("=" * 88)

    for case in TEST_CASES:
        started = time.perf_counter()

        results = retrieve_chunks(
        question=case.question,
        limit=3,
        evaluation_mode=True,
    )

        latency_ms = (
            time.perf_counter()
            - started
        ) * 1000

        latency_total_ms += latency_ms

        rank = _find_rank(
            results=results,
            acceptable_title_terms=(
                case.acceptable_title_terms
            ),
        )

        if rank == 1:
            hit_at_1 += 1

        if (
            rank is not None
            and rank <= 3
        ):
            hit_at_3 += 1

        if rank is not None:
            reciprocal_rank_total += (
                1.0 / rank
            )

        if results:
            top = results[0]

            semantic_total += float(
                top.get(
                    "semantic_score",
                    0.0,
                )
            )

            content_bonus_total += float(
                top.get(
                    "keyword_bonus",
                    0.0,
                )
            )

            title_bonus_total += float(
                top.get(
                    "title_bonus",
                    0.0,
                )
            )

            scored_result_count += 1

        top_title = (
            results[0].get("title")
            if results
            else None
        )

        status = (
            "PASS"
            if (
                rank is not None
                and rank <= 3
            )
            else "FAIL"
        )

        print(
            f"Question : {case.question}"
        )
        print(
            "Expected : "
            + " OR ".join(
                case.acceptable_title_terms
            )
        )
        print(
            f"Top title: {top_title}"
        )
        print(
            f"Rank     : {rank}"
        )
        print(
            f"Latency  : {latency_ms:.2f} ms"
        )
        print(
            f"Result   : {status}"
        )
        print("-" * 88)

        if (
            rank is None
            or rank > 3
        ):
            failures.append(
                {
                    "question": (
                        case.question
                    ),
                    "expected": (
                        case.acceptable_title_terms
                    ),
                    "top_title": (
                        top_title
                    ),
                    "rank": rank,
                }
            )

    total = len(
        TEST_CASES
    )

    hit_at_1_rate = (
        hit_at_1 / total
        if total
        else 0.0
    )

    hit_at_3_rate = (
        hit_at_3 / total
        if total
        else 0.0
    )

    mean_reciprocal_rank = (
        reciprocal_rank_total / total
        if total
        else 0.0
    )

    average_latency_ms = (
        latency_total_ms / total
        if total
        else 0.0
    )

    average_semantic_score = (
        semantic_total
        / scored_result_count
        if scored_result_count
        else 0.0
    )

    average_content_bonus = (
        content_bonus_total
        / scored_result_count
        if scored_result_count
        else 0.0
    )

    average_title_bonus = (
        title_bonus_total
        / scored_result_count
        if scored_result_count
        else 0.0
    )

    print("=" * 88)
    print("Summary")
    print("=" * 88)
    print(
        f"Questions evaluated : {total}"
    )
    print(
        f"Hit@1               : "
        f"{hit_at_1}/{total} "
        f"({hit_at_1_rate:.1%})"
    )
    print(
        f"Hit@3               : "
        f"{hit_at_3}/{total} "
        f"({hit_at_3_rate:.1%})"
    )
    print(
        "Mean reciprocal rank: "
        f"{mean_reciprocal_rank:.3f}"
    )
    print(
        "Average latency     : "
        f"{average_latency_ms:.2f} ms"
    )
    print(
        "Average semantic    : "
        f"{average_semantic_score:.4f}"
    )
    print(
        "Average content bonus: "
        f"{average_content_bonus:.4f}"
    )
    print(
        "Average title bonus : "
        f"{average_title_bonus:.4f}"
    )
    print(
        f"Failures            : "
        f"{len(failures)}"
    )

    if failures:
        print("-" * 88)
        print("Failure details")

        for failure in failures:
            print(
                f"- {failure}"
            )

    return {
        "questions": total,
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hit_at_1_rate": (
            hit_at_1_rate
        ),
        "hit_at_3_rate": (
            hit_at_3_rate
        ),
        "mean_reciprocal_rank": (
            mean_reciprocal_rank
        ),
        "average_latency_ms": (
            average_latency_ms
        ),
        "average_semantic_score": (
            average_semantic_score
        ),
        "average_content_bonus": (
            average_content_bonus
        ),
        "average_title_bonus": (
            average_title_bonus
        ),
        "failures": failures,
        "success": not failures,
    }


if __name__ == "__main__":
    result = evaluate()

    if not result["success"]:
        raise SystemExit(1)