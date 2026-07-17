from __future__ import annotations

from app.services.retrieval_explanation_service import (
    RetrievalExplanation,
    explain_retrieval,
)


def _assert(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(
            message
        )


def test_entity_aware_explanation() -> None:
    selected_chunk = {
        "title": "Dr Rajkumar",
        "semantic_score": 0.81,
        "keyword_bonus": 0.08,
        "title_bonus": 0.08,
        "entity_title_bonus": 0.08,
        "raw_score": 1.05,
        "score": 1.0,
        "source_name": "curated",
        "source_url": (
            "https://example.com/dr-rajkumar"
        ),
    }

    explanation = explain_retrieval(
        selected_chunk=selected_chunk,
        result_count=1,
    )

    _assert(
        isinstance(
            explanation,
            RetrievalExplanation,
        ),
        "Expected an immutable RetrievalExplanation model.",
    )

    _assert(
        explanation.selected_title
        == "Dr Rajkumar",
        "Selected title was not preserved.",
    )

    _assert(
        explanation.entity_title_bonus
        == 0.08,
        "Entity title bonus was not preserved.",
    )

    _assert(
        (
            "Canonical entity matched "
            "the document title."
        )
        in explanation.reasons,
        (
            "Entity-aware explanation reason "
            "was not generated."
        ),
    )

    _assert(
        (
            "Retriever retained one clear "
            "top result."
        )
        in explanation.reasons,
        (
            "Single-result explanation reason "
            "was not generated."
        ),
    )

    _assert(
        explanation.raw_score == 1.05,
        "Raw score must remain unbounded.",
    )

    _assert(
        explanation.bounded_score == 1.0,
        "Bounded score was not preserved.",
    )


def test_multiple_context_explanation() -> None:
    selected_chunk = {
        "title": "Madhwacharya",
        "semantic_score": 0.77,
        "keyword_bonus": 0.0,
        "title_bonus": 0.0,
        "entity_title_bonus": 0.0,
        "raw_score": 0.77,
        "score": 0.77,
        "source_name": "Wikipedia",
        "source_url": None,
    }

    explanation = explain_retrieval(
        selected_chunk=selected_chunk,
        result_count=3,
    )

    _assert(
        (
            "Document had semantic similarity "
            "with the question."
        )
        in explanation.reasons,
        (
            "Semantic explanation reason "
            "was not generated."
        ),
    )

    _assert(
        (
            "Retriever retained multiple "
            "relevant context chunks."
        )
        in explanation.reasons,
        (
            "Multiple-context explanation "
            "reason was not generated."
        ),
    )

    _assert(
        not any(
            "Canonical entity" in reason
            for reason in explanation.reasons
        ),
        (
            "Entity reason must not be emitted "
            "without an entity bonus."
        ),
    )

    _assert(
        explanation.provenance
        == "not_recorded",
        (
            "Missing provenance should use the "
            "documented fallback."
        ),
    )


def test_safe_defaults() -> None:
    explanation = explain_retrieval(
        selected_chunk={},
        result_count=0,
    )

    _assert(
        explanation.selected_title == "",
        "Missing title should default to empty.",
    )

    _assert(
        explanation.semantic_score == 0.0,
        "Missing semantic score should default to zero.",
    )

    _assert(
        explanation.raw_score == 0.0,
        "Missing raw score should default to zero.",
    )

    _assert(
        explanation.source_name == "unknown",
        "Missing source should default to unknown.",
    )

    _assert(
        explanation.provenance
        == "not_recorded",
        (
            "Missing provenance should use the "
            "documented fallback."
        ),
    )


def run() -> None:
    tests = [
        (
            "Entity-aware explanation",
            test_entity_aware_explanation,
        ),
        (
            "Multiple-context explanation",
            test_multiple_context_explanation,
        ),
        (
            "Safe defaults",
            test_safe_defaults,
        ),
    ]

    passed = 0

    print("=" * 72)
    print("Retrieval Explanation Service Tests")
    print("=" * 72)

    for name, test in tests:
        try:
            test()
        except Exception as error:
            print(
                f"{name:<40} FAIL"
            )
            print(
                f"  {error}"
            )
            continue

        print(
            f"{name:<40} PASS"
        )
        passed += 1

    print("-" * 72)
    print(
        f"Passed: {passed}"
    )
    print(
        f"Failed: {len(tests) - passed}"
    )

    if passed != len(tests):
        raise SystemExit(1)


if __name__ == "__main__":
    run()
