"""
Entity Classification Test
==========================

Purpose
-------
Validate deterministic classification of accepted provider metadata.

Phase 6.2A supports:

    Wikidata P31 Q5
            ↓
          PERSON

Unknown, malformed, or missing metadata must safely fall back to:

    GENERAL
"""

from app.models.knowledge_entity import KnowledgeEntity
from app.services.entity_classification_service import (
    ENTITY_TYPE_GENERAL,
    ENTITY_TYPE_PERSON,
    classify_entity,
    determine_entity_type,
)


def _build_entity(
    entity_type: str = ENTITY_TYPE_GENERAL,
) -> KnowledgeEntity:
    """
    Build a minimal immutable entity for classification tests.
    """

    return KnowledgeEntity(
        original_query="Kempegowda",
        normalized_query="Kempegowda",
        resolved_topic="Kempe Gowda I",
        display_name="Kempe Gowda I",
        entity_type=entity_type,
        domain="history",
        confidence=0.90,
        resolution_method=(
            "normalized_input+provider_evidence"
        ),
    )


def run() -> None:
    """
    Execute deterministic classification scenarios.
    """

    person_sources = [
        {
            "provider": "Wikidata",
            "trust_level": "high",
            "metadata": {
                "entity_id": "Q6387049",
                "instance_of_ids": [
                    "Q5",
                ],
            },
        }
    ]

    person_type = determine_entity_type(
        person_sources
    )

    assert person_type == ENTITY_TYPE_PERSON, (
        "Q5 must map to PERSON."
    )

    original_entity = _build_entity()

    classified_entity = classify_entity(
        entity=original_entity,
        sources=person_sources,
    )

    assert classified_entity.entity_type == (
        ENTITY_TYPE_PERSON
    )

    assert original_entity.entity_type == (
        ENTITY_TYPE_GENERAL
    ), (
        "The original immutable entity must not change."
    )

    assert classified_entity is not original_entity, (
        "Classification must return a new entity when "
        "the type changes."
    )

    unknown_sources = [
        {
            "provider": "Wikidata",
            "trust_level": "high",
            "metadata": {
                "instance_of_ids": [
                    "Q999999999",
                ],
            },
        }
    ]

    unknown_type = determine_entity_type(
        unknown_sources
    )

    assert unknown_type == ENTITY_TYPE_GENERAL, (
        "Unknown Wikidata types must safely fall "
        "back to GENERAL."
    )

    malformed_sources = [
        {
            "provider": "Wikidata",
            "metadata": {
                "instance_of_ids": (
                    "Q5"
                ),
            },
        },
        {
            "provider": "Unknown",
            "metadata": None,
        },
        "invalid source",
    ]

    malformed_type = determine_entity_type(
        malformed_sources
    )

    assert malformed_type == ENTITY_TYPE_GENERAL, (
        "Malformed metadata must not cause speculative "
        "classification."
    )

    previously_classified = _build_entity(
        entity_type="PLACE"
    )

    preserved_entity = classify_entity(
        entity=previously_classified,
        sources=person_sources,
    )

    assert preserved_entity is previously_classified, (
        "Existing non-GENERAL classifications must "
        "be preserved."
    )

    assert preserved_entity.entity_type == "PLACE"

    print("=" * 72)
    print("Entity Classification Test")
    print("=" * 72)
    print("Q5 mapping                    : PERSON")
    print("Immutable replacement         : PASS")
    print("Unknown type fallback         : GENERAL")
    print("Malformed metadata fallback   : GENERAL")
    print("Existing type preservation    : PASS")
    print("=" * 72)
    print("Entity classification service : PASS")


if __name__ == "__main__":
    run()
