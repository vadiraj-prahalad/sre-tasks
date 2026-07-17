from app.models.knowledge_entity import (
    KnowledgeEntity,
)
from app.services.retriever_service import (
    retrieve_chunks,
)


def run() -> None:
    rajkumar_entity = KnowledgeEntity(
        original_query="ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?",
        normalized_query=(
            "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?"
        ),
        resolved_topic="Dr Rajkumar",
        display_name="Dr Rajkumar",
        domain="cinema",
        confidence=1.0,
        resolution_method="alias_lookup",
    )

    relationship_entity = KnowledgeEntity(
        original_query=(
            "ಉಡುಪಿ ಮಠದ ಜೊತೆ ಮಧ್ವರ ಸಂಬಂಧ ಏನು"
        ),
        normalized_query=(
            "ಉಡುಪಿ ಮಠದ ಜೊತೆ "
            "ಮಧ್ವಾಚಾರ್ಯರ ಸಂಬಂಧ ಏನು"
        ),
        resolved_topic=(
            "ಉಡುಪಿ ಮಠದ ಜೊತೆ "
            "ಮಧ್ವಾಚಾರ್ಯರ ಸಂಬಂಧ"
        ),
        display_name=(
            "ಉಡುಪಿ ಮಠದ ಜೊತೆ "
            "ಮಧ್ವಾಚಾರ್ಯರ ಸಂಬಂಧ"
        ),
        domain="religion",
        confidence=0.5,
        resolution_method="normalized_input",
    )

    rajkumar_results = retrieve_chunks(
        question=(
            "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?"
        ),
        entity=rajkumar_entity,
        limit=3,
        evaluation_mode=True,
    )

    relationship_results = retrieve_chunks(
        question=(
            "ಉಡುಪಿ ಮಠದ ಜೊತೆ "
            "ಮಧ್ವಾಚಾರ್ಯರ ಸಂಬಂಧ ಏನು"
        ),
        entity=relationship_entity,
        limit=3,
        evaluation_mode=True,
    )

    rajkumar_top_title = (
        rajkumar_results[0]["title"]
        if rajkumar_results
        else ""
    )

    rajkumar_bonus = (
        rajkumar_results[0].get(
            "entity_title_bonus",
            0.0,
        )
        if rajkumar_results
        else 0.0
    )

    relationship_bonus = (
        relationship_results[0].get(
            "entity_title_bonus",
            0.0,
        )
        if relationship_results
        else 0.0
    )

    checks = {
        "Rajkumar ranks first": (
            "Rajkumar"
            in rajkumar_top_title
        ),
        "Canonical title bonus applied": (
            rajkumar_bonus == 0.08
        ),
        "Low-confidence entity ignored": (
            relationship_bonus == 0.0
        ),
        "Score remains bounded": (
            all(
                0.0
                <= result["score"]
                <= 1.0
                for result
                in rajkumar_results
            )
        ),
    }

    print("=" * 76)
    print("Entity-Aware Retrieval Test")
    print("=" * 76)

    for name, passed in checks.items():
        print(
            f"{name:<34}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    print("=" * 76)

    failures = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    if failures:
        raise AssertionError(
            "Entity-aware retrieval regression: "
            + ", ".join(failures)
        )

    print(
        "Entity-aware retrieval service : PASS"
    )
    print("=" * 76)


if __name__ == "__main__":
    run()