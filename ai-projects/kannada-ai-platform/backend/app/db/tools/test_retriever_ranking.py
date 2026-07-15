"""
Retriever Ranking Test
======================

Protects entity-aware retrieval behavior.

Purpose
-------
Verify that:

1. Exact entity-name matches rank above semantically similar entities.
2. Existing successful retrieval cases do not regress.
3. Generic question words do not create useful lexical bonus.
4. Final retrieval scores remain between 0 and 1.
"""

from app.services.retriever_service import (
    keyword_bonus,
    retrieve_chunks,
)


TEST_CASES = [
    {
        "question": "ಕುವೆಂಪು ಯಾರು?",
        "expected_title_contains": "ಕುವೆಂಪು",
    },
    {
        "question": "ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?",
        "expected_title_contains": "ವಿಷ್ಣುವರ್ಧನ್",
    },
    {
        "question": "ಪುರಂದರ ದಾಸರ ಕೊಡುಗೆ",
        "expected_title_contains": "ಪುರಂದರ ದಾಸರ ಕೊಡುಗೆ",
    },
    {
        "question": "ಮಧ್ವಾಚಾರ್ಯರು ಯಾರು?",
        "expected_title_contains": "ಮಧ್ವಾಚಾರ್ಯರು",
    },
]


def run() -> None:
    failures: list[str] = []

    print("=" * 80)
    print("Retriever Ranking Test")
    print("=" * 80)

    for test_case in TEST_CASES:
        question = test_case["question"]
        expected_title = (
            test_case[
                "expected_title_contains"
            ]
        )

        results = retrieve_chunks(
            question=question,
            limit=3,
        )

        if not results:
            failures.append(
                f"No retrieval result for: {question}"
            )

            print(
                f"Question: {question}"
            )
            print(
                "Result  : FAIL — no chunks returned"
            )
            print("-" * 80)
            continue

        top_result = results[0]
        top_title = (
            top_result.get("title") or ""
        )

        top_score = float(
            top_result.get("score", 0.0)
        )

        title_matched = (
            expected_title in top_title
        )

        score_bounded = (
            0.0 <= top_score <= 1.0
        )

        print(
            f"Question : {question}"
        )
        print(
            f"Expected : {expected_title}"
        )
        print(
            f"Top title: {top_title}"
        )
        print(
            f"Score    : {top_score:.4f}"
        )
        print(
            "Ranking  : "
            f"{'PASS' if title_matched else 'FAIL'}"
        )
        print(
            "Score cap: "
            f"{'PASS' if score_bounded else 'FAIL'}"
        )
        print("-" * 80)

        if not title_matched:
            failures.append(
                (
                    f"Expected title containing "
                    f"'{expected_title}' for "
                    f"'{question}', but received "
                    f"'{top_title}'."
                )
            )

        if not score_bounded:
            failures.append(
                (
                    f"Score {top_score:.4f} is outside "
                    f"the supported range for "
                    f"'{question}'."
                )
            )

    generic_bonus = keyword_bonus(
    search_text="ಯಾರು?",
    target_text="ವಿಷ್ಣುವರ್ಧನ್ ಯಾರು?",
    )

    generic_bonus_ignored = (
        generic_bonus == 0.0
    )

    print(
        "Generic question-word bonus: "
        f"{generic_bonus:.4f}"
    )
    print(
        "Generic words ignored       : "
        f"{'PASS' if generic_bonus_ignored else 'FAIL'}"
    )
    print("=" * 80)

    if not generic_bonus_ignored:
        failures.append(
            (
                "Generic question word 'ಯಾರು' "
                "must not create keyword bonus."
            )
        )

    if failures:
        print("Retriever ranking service: FAIL")
        print("=" * 80)

        for failure in failures:
            print(f"- {failure}")

        raise AssertionError(
            "Retriever ranking regression detected."
        )

    print("Retriever ranking service: PASS")


if __name__ == "__main__":
    run()