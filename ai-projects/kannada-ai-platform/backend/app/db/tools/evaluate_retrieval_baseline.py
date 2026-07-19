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
from app.services.retriever_service import (
    retrieve_chunks,
)
from app.services.entity_resolution_service import (
    resolve_entity,
)
from app.db.tools.benchmark_cases import (
    TEST_CASES,
)


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

    top_source_counts: dict[str, int] = {}
    top_provenance_counts: dict[str, int] = {}

    print("=" * 88)
    print("Retrieval Baseline Evaluation")
    print("=" * 88)

    for case in TEST_CASES:
        started = time.perf_counter()

        entity = resolve_entity(
            topic=case.question,
            category="general",
        )

        results = retrieve_chunks(
            question=case.question,
            limit=3,
            entity=entity,
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

        top_result = (
            results[0]
            if results
            else {}
        )

        top_title = (
            top_result.get("title")
            if top_result
            else None
        )

        top_source_name = str(
            top_result.get(
                "source_name",
                "none",
            )
        )

        top_provenance = str(
            top_result.get(
                "source_url",
            )
            or "not_recorded"
        )

        top_semantic_score = float(
            top_result.get(
                "semantic_score",
                0.0,
            )
        )

        top_content_bonus = float(
            top_result.get(
                "keyword_bonus",
                0.0,
            )
        )

        top_title_bonus = float(
            top_result.get(
                "title_bonus",
                0.0,
            )
        )

        top_raw_score = float(
            top_result.get(
                "raw_score",
                top_result.get(
                    "score",
                    0.0,
                ),
            )
        )

        top_bounded_score = float(
            top_result.get(
                "score",
                0.0,
            )
        )

        if results:
            top_source_counts[
                top_source_name
            ] = (
                top_source_counts.get(
                    top_source_name,
                    0,
                )
                + 1
            )

            top_provenance_counts[
                top_provenance
            ] = (
                top_provenance_counts.get(
                    top_provenance,
                    0,
                )
                + 1
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
            "Entity   : "
            f"{entity.preferred_name} | "
            f"method={entity.resolution_method} | "
            f"confidence={entity.confidence:.2f}"
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
            f"Semantic : {top_semantic_score:.4f}"
        )
        print(
            f"Content  : {top_content_bonus:.4f}"
        )
        print(
            f"Title    : {top_title_bonus:.4f}"
        )
        print(
            f"Raw score: {top_raw_score:.4f}"
        )
        print(
            f"Score    : {top_bounded_score:.4f}"
        )
        print(
            f"Source   : {top_source_name}"
        )
        print(
            f"Provenance: {top_provenance}"
        )
        print(
            f"Latency  : {latency_ms:.2f} ms"
        )
        print(
            f"Result   : {status}"
        )

        if status == "FAIL":
            print("\nTop 3 Retrieved Candidates")
            print("-" * 40)

            for index, candidate in enumerate(results[:3], start=1):
                print(f"{index}. {candidate['title']}")
                print(f"   Raw Score : {candidate['raw_score']:.4f}")
                print(f"   Semantic  : {candidate['semantic_score']:.4f}")
                print(f"   Content   : {candidate['keyword_bonus']:.4f}")
                print(f"   Title     : {candidate['title_bonus']:.4f}")
                print(
                    "   Entity    : "
                    f"{candidate['entity_title_bonus']:.4f}"
                )
                print()

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
            "semantic_score": round(
                top_semantic_score,
                4,
            ),
            "content_bonus": round(
                top_content_bonus,
                4,
            ),
            "title_bonus": round(
                top_title_bonus,
                4,
            ),
            "raw_score": round(
                top_raw_score,
                4,
            ),
            "bounded_score": round(
                top_bounded_score,
                4,
            ),
            "source_name": (
                top_source_name
            ),
            "provenance": (
                top_provenance
            ),
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
    print("-" * 88)
    print("Top-result source distribution")

    for source_name, count in sorted(
        top_source_counts.items()
    ):
        print(
            f"- {source_name}: {count}"
        )

    print("-" * 88)
    print("Top-result provenance distribution")

    for provenance, count in sorted(
        top_provenance_counts.items()
    ):
        print(
            f"- {provenance}: {count}"
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
        "top_source_counts": (
        top_source_counts
        ),
        "top_provenance_counts": (
            top_provenance_counts
        ),
        "failures": failures,
        "success": not failures,
    }


if __name__ == "__main__":
    result = evaluate()

    if not result["success"]:
        raise SystemExit(1)