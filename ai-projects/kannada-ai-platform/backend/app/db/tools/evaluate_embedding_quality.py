from __future__ import annotations

from app.services.retriever_service import (
    retrieve_chunks,
)


TEST_CASES = [
    {
        "question": "ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?",
        "expected_titles": (
            "Dr Rajkumar and Kannada Culture",
        ),
    },
    {
        "question": "ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?",
        "expected_titles": (
            "ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?",
        ),
    },
    {
        "question": "ಕುವೆಂಪು ಯಾರು?",
        "expected_titles": (
            "ಕುವೆಂಪು ಯಾರು?",
            "Kuvempu and Kannada Literature",
        ),
    },
    {
        "question": "ಪುರಂದರ ದಾಸರು ಯಾರು?",
        "expected_titles": (
            "ಪುರಂದರ ದಾಸರು ಯಾರು?",
        ),
    },
    {
        "question": "ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?",
        "expected_titles": (
            "ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?",
        ),
    },
    {
        "question": "ಮೈಸೂರು ಅರಮನೆ ಬಗ್ಗೆ ಹೇಳಿ",
        "expected_titles": (
            "ಮೈಸೂರು ಅರಮನೆ ಬಗ್ಗೆ ಹೇಳಿ",
        ),
    },
]


def _find_expected_rank(
    results: list[dict],
    expected_titles: tuple[str, ...],
) -> int | None:
    normalized_expected = {
        title.casefold().strip()
        for title in expected_titles
    }

    for rank, result in enumerate(
        results,
        start=1,
    ):
        title = str(
            result.get("title") or ""
        ).casefold().strip()

        if title in normalized_expected:
            return rank

    return None


def _format_score(
    value: object,
) -> str:
    if not isinstance(
        value,
        (int, float),
    ):
        return "n/a"

    return f"{value:.4f}"


def main() -> None:
    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0
    reciprocal_rank_total = 0.0

    print("=" * 88)
    print("Embedding Quality Baseline")
    print("=" * 88)

    for test_case in TEST_CASES:
        question = test_case["question"]
        expected_titles = test_case[
            "expected_titles"
        ]

        # No entity is supplied intentionally.
        # This evaluation measures embedding quality,
        # not hybrid or entity-aware ranking.
        results = retrieve_chunks(
            question=question,
            limit=100,
            entity=None,
            evaluation_mode=True,
        )

        expected_rank = _find_expected_rank(
            results=results,
            expected_titles=expected_titles,
        )

        top_result = (
            results[0]
            if results
            else {}
        )

        if expected_rank == 1:
            hit_at_1 += 1

        if (
            expected_rank is not None
            and expected_rank <= 3
        ):
            hit_at_3 += 1

        if (
            expected_rank is not None
            and expected_rank <= 5
        ):
            hit_at_5 += 1

        if expected_rank is not None:
            reciprocal_rank_total += (
                1.0 / expected_rank
            )

        expected_result = (
            results[expected_rank - 1]
            if expected_rank is not None
            else {}
        )

        print(f"Question      : {question}")
        print(
            "Expected      : "
            + " OR ".join(expected_titles)
        )
        print(
            "Expected rank : "
            + (
                str(expected_rank)
                if expected_rank is not None
                else "Not found"
            )
        )
        print(
            "Expected score: "
            + _format_score(
                expected_result.get(
                    "semantic_score"
                )
            )
        )
        print(
            "Top title     : "
            + str(
                top_result.get("title")
                or "No result"
            )
        )
        print(
            "Top semantic  : "
            + _format_score(
                top_result.get(
                    "semantic_score"
                )
            )
        )
        print("-" * 88)

    total = len(TEST_CASES)

    mean_reciprocal_rank = (
        reciprocal_rank_total / total
        if total
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
        f"({hit_at_1 / total:.1%})"
    )
    print(
        f"Hit@3               : "
        f"{hit_at_3}/{total} "
        f"({hit_at_3 / total:.1%})"
    )
    print(
        f"Hit@5               : "
        f"{hit_at_5}/{total} "
        f"({hit_at_5 / total:.1%})"
    )
    print(
        "Mean reciprocal rank: "
        f"{mean_reciprocal_rank:.3f}"
    )


if __name__ == "__main__":
    main()