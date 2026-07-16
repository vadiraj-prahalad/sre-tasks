from app.models.knowledge_entity import (
    KnowledgeEntity,
)
from app.services import rag_service


def run() -> None:
    captured: dict = {}

    original_retrieve_chunks = (
        rag_service.retrieve_chunks
    )
    original_should_use_direct_answer = (
        rag_service.should_use_direct_answer
    )
    original_compose_direct_answer = (
        rag_service.compose_direct_answer
    )
    original_clean_final_answer = (
        rag_service.clean_final_answer
    )

    entity = KnowledgeEntity(
        original_query="ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?",
        normalized_query="ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
        resolved_topic="Dr Rajkumar",
        display_name="Dr Rajkumar",
        domain="cinema",
        confidence=1.0,
        resolution_method="alias_lookup",
    )

    def fake_retrieve_chunks(
        question: str,
        limit: int = 3,
        *,
        entity: KnowledgeEntity | None = None,
        evaluation_mode: bool = False,
    ) -> list[dict]:
        captured["question"] = question
        captured["limit"] = limit
        captured["entity"] = entity
        captured["evaluation_mode"] = (
            evaluation_mode
        )

        return [
            {
                "chunk_text": (
                    "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಕನ್ನಡ "
                    "ಚಿತ್ರರಂಗದ ಪ್ರಸಿದ್ಧ ನಟರು."
                ),
                "score": 0.95,
                "raw_score": 0.95,
                "semantic_score": 0.85,
                "keyword_bonus": 0.05,
                "title_bonus": 0.05,
                "title": "Dr Rajkumar",
                "source_name": (
                    "Curated Internal Knowledge"
                ),
                "source_url": None,
            }
        ]

    try:
        rag_service.retrieve_chunks = (
            fake_retrieve_chunks
        )

        rag_service.should_use_direct_answer = (
            lambda question: True
        )

        rag_service.compose_direct_answer = (
            lambda question, context: context
        )

        rag_service.clean_final_answer = (
            lambda answer: answer
        )

        result = (
            rag_service.answer_from_rag_with_trace(
                question="ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
                entity=entity,
            )
        )

        checks = {
            "Entity forwarded": (
                captured.get("entity")
                is entity
            ),
            "Question forwarded": (
                captured.get("question")
                == "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?"
            ),
            "Entity trace present": any(
                item.get("step")
                == "Canonical Entity"
                for item in result["trace"]
            ),
            "Answer preserved": bool(
                result.get("answer")
            ),
        }

        print("=" * 72)
        print("Runtime Entity Flow Test")
        print("=" * 72)

        for name, passed in checks.items():
            print(
                f"{name:<28}: "
                f"{'PASS' if passed else 'FAIL'}"
            )

        print("=" * 72)

        failures = [
            name
            for name, passed
            in checks.items()
            if not passed
        ]

        if failures:
            raise AssertionError(
                "Runtime entity-flow regression: "
                + ", ".join(failures)
            )

        print("Runtime entity flow       : PASS")
        print("=" * 72)

    finally:
        rag_service.retrieve_chunks = (
            original_retrieve_chunks
        )

        rag_service.should_use_direct_answer = (
            original_should_use_direct_answer
        )

        rag_service.compose_direct_answer = (
            original_compose_direct_answer
        )

        rag_service.clean_final_answer = (
            original_clean_final_answer
        )


if __name__ == "__main__":
    run()