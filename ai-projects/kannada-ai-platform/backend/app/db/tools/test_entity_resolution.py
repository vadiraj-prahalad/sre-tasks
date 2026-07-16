from app.services.entity_resolution_service import (
    resolve_entity,
)


TEST_CASES = [
    {
        "topic": "Basavanna",
        "category": "religion",
        "expected_resolved": "Basava",
        "expected_confidence": 1.0,
        "expected_method": "alias_lookup",
    },
    {
        "topic": "Basaveshwara",
        "category": "religion",
        "expected_resolved": "Basava",
        "expected_confidence": 1.0,
        "expected_method": "alias_lookup",
    },
    {
        "topic": "Basava",
        "category": "religion",
        "expected_resolved": "Basava",
        "expected_confidence": 1.0,
        "expected_method": "alias_lookup",
    },
    {
        "topic": "Mysore Palace",
        "category": "location",
        "expected_resolved": "Mysore Palace",
        "expected_confidence": 1.0,
        "expected_method": "alias_lookup",
    },
    {
        "topic": "Bangalore",
        "category": "location",
        "expected_resolved": "Bengaluru",
        "expected_confidence": 1.0,
        "expected_method": "alias_lookup",
    },
    {
        "topic": "ಡಾ ರಾಜಕುಮಾರ್ ಯಾರು?",
        "category": "cinema",
        "expected_resolved": "Dr Rajkumar",
        "expected_confidence": 1.0,
        "expected_method": "alias_lookup",
    },
    {
        "topic": "Unknown Topic",
        "category": "general",
        "expected_resolved": "Unknown Topic",
        "expected_confidence": 0.5,
        "expected_method": "normalized_input",
    },
]


def run() -> None:
    failures: list[str] = []

    print("=" * 70)
    print("Entity Resolution Test")
    print("=" * 70)

    for test in TEST_CASES:
        topic = test["topic"]
        category = test["category"]

        entity = resolve_entity(
            topic=topic,
            category=category,
        )

        entity_changed = (
            entity.resolved_topic
            != entity.original_query
        )

        resolved_pass = (
            entity.resolved_topic
            == test["expected_resolved"]
        )

        confidence_pass = (
            entity.confidence
            == test["expected_confidence"]
        )

        method_pass = (
            entity.resolution_method
            == test["expected_method"]
        )

        case_passed = (
            resolved_pass
            and confidence_pass
            and method_pass
        )

        print(
            f"Input          : "
            f"{entity.original_query}"
        )
        print(
            f"Normalized     : "
            f"{entity.normalized_query}"
        )
        print(
            f"Resolved       : "
            f"{entity.resolved_topic}"
        )
        print(
            f"Preferred Name : "
            f"{entity.preferred_name}"
        )
        print(
            f"Changed        : "
            f"{entity_changed}"
        )
        print(
            f"Entity Type    : "
            f"{entity.entity_type}"
        )
        print(
            f"Domain         : "
            f"{entity.domain}"
        )
        print(
            f"Confidence     : "
            f"{entity.confidence}"
        )
        print(
            f"Method         : "
            f"{entity.resolution_method}"
        )
        print(
            "Result         : "
            f"{'PASS' if case_passed else 'FAIL'}"
        )
        print("-" * 70)

        if not resolved_pass:
            failures.append(
                (
                    f"{topic}: expected resolved topic "
                    f"'{test['expected_resolved']}', "
                    f"received "
                    f"'{entity.resolved_topic}'."
                )
            )

        if not confidence_pass:
            failures.append(
                (
                    f"{topic}: expected confidence "
                    f"{test['expected_confidence']}, "
                    f"received "
                    f"{entity.confidence}."
                )
            )

        if not method_pass:
            failures.append(
                (
                    f"{topic}: expected method "
                    f"'{test['expected_method']}', "
                    f"received "
                    f"'{entity.resolution_method}'."
                )
            )

    print("=" * 70)

    if failures:
        print(
            "Entity resolution service : FAIL"
        )
        print("=" * 70)

        for failure in failures:
            print(
                f"- {failure}"
            )

        raise AssertionError(
            "Entity resolution regression detected."
        )

    print(
        "Entity resolution service : PASS"
    )
    print("=" * 70)


if __name__ == "__main__":
    run()