"""
Entity Classification Test
==========================

Purpose
-------
Validate deterministic classification of accepted provider metadata.

Phase 6.2B supports:

    Wikidata P31 Q5
            ↓
          PERSON

    Wikidata P31 Q515
            ↓
           PLACE

    Wikidata P31 Q43229
            ↓
       ORGANIZATION

Unknown, malformed, or missing metadata must safely fall back to:

    GENERAL
"""

from app.models.knowledge_entity import KnowledgeEntity
from app.services.entity_classification_service import (
    ENTITY_TYPE_GENERAL,
    ENTITY_TYPE_ORGANIZATION,
    ENTITY_TYPE_PERSON,
    ENTITY_TYPE_PLACE,
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
        original_query="Test Topic",
        normalized_query="Test Topic",
        resolved_topic="Test Topic",
        display_name="Test Topic",
        entity_type=entity_type,
        domain="general",
        confidence=0.90,
        resolution_method=(
            "normalized_input+provider_evidence"
        ),
    )


def run() -> None:
    """
    Execute deterministic classification scenarios.

    Covered behavior:
    - Q5 maps to PERSON.
    - Q515 maps to PLACE.
    - Q43229 maps to ORGANIZATION.
    - Unknown IDs fall back to GENERAL.
    - Malformed metadata falls back to GENERAL.
    - Existing non-GENERAL types are preserved.
    - Multiple P31 values select the first supported mapping.
    - Immutable entities are replaced rather than modified.
    """

    # ------------------------------------------------------------------
    # PERSON classification
    # ------------------------------------------------------------------

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

    classified_person = classify_entity(
        entity=original_entity,
        sources=person_sources,
    )

    assert classified_person.entity_type == (
        ENTITY_TYPE_PERSON
    )

    assert original_entity.entity_type == (
        ENTITY_TYPE_GENERAL
    ), (
        "The original immutable entity must not change."
    )

    assert classified_person is not original_entity, (
        "Classification must return a new entity when "
        "the type changes."
    )

    # ------------------------------------------------------------------
    # PLACE classification
    # ------------------------------------------------------------------

    place_sources = [
        {
            "provider": "Wikidata",
            "trust_level": "high",
            "metadata": {
                "entity_id": "Q64",
                "instance_of_ids": [
                    "Q515",
                ],
            },
        }
    ]

    place_type = determine_entity_type(
        place_sources
    )

    assert place_type == ENTITY_TYPE_PLACE, (
        "Q515 must map to PLACE."
    )

    classified_place = classify_entity(
        entity=_build_entity(),
        sources=place_sources,
    )

    assert classified_place.entity_type == (
        ENTITY_TYPE_PLACE
    )

    # ------------------------------------------------------------------
    # ORGANIZATION classification
    # ------------------------------------------------------------------

    organization_sources = [
        {
            "provider": "Wikidata",
            "trust_level": "high",
            "metadata": {
                "entity_id": "Q123456",
                "instance_of_ids": [
                    "Q43229",
                ],
            },
        }
    ]

    organization_type = determine_entity_type(
        organization_sources
    )

    assert organization_type == (
        ENTITY_TYPE_ORGANIZATION
    ), (
        "Q43229 must map to ORGANIZATION."
    )

    classified_organization = classify_entity(
        entity=_build_entity(),
        sources=organization_sources,
    )

    assert classified_organization.entity_type == (
        ENTITY_TYPE_ORGANIZATION
    )

    # ------------------------------------------------------------------
    # Unknown type fallback
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Malformed metadata fallback
    # ------------------------------------------------------------------

    malformed_sources = [
        {
            "provider": "Wikidata",
            "metadata": {
                "instance_of_ids": "Q5",
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

    # ------------------------------------------------------------------
    # Existing classification preservation
    # ------------------------------------------------------------------

    previously_classified = _build_entity(
        entity_type=ENTITY_TYPE_PLACE
    )

    preserved_entity = classify_entity(
        entity=previously_classified,
        sources=person_sources,
    )

    assert preserved_entity is previously_classified, (
        "Existing non-GENERAL classifications must "
        "be preserved."
    )

    assert preserved_entity.entity_type == (
        ENTITY_TYPE_PLACE
    )

    # ------------------------------------------------------------------
    # Multiple P31 values
    # ------------------------------------------------------------------

    multiple_type_sources = [
        {
            "provider": "Wikidata",
            "trust_level": "high",
            "metadata": {
                "instance_of_ids": [
                    "Q999999999",
                    "Q43229",
                    "Q515",
                ],
            },
        }
    ]

    multiple_type = determine_entity_type(
        multiple_type_sources
    )

    assert multiple_type == (
        ENTITY_TYPE_ORGANIZATION
    ), (
        "The first supported deterministic mapping "
        "must be selected."
    )

    # ------------------------------------------------------------------
    # Test report
    # ------------------------------------------------------------------

    print("=" * 72)
    print("Entity Classification Test")
    print("=" * 72)
    print("Q5 mapping                    : PERSON")
    print("Q515 mapping                  : PLACE")
    print("Q43229 mapping                : ORGANIZATION")
    print("Immutable replacement         : PASS")
    print("Unknown type fallback         : GENERAL")
    print("Malformed metadata fallback   : GENERAL")
    print("Existing type preservation    : PASS")
    print("Multiple P31 handling         : PASS")
    print("=" * 72)
    print("Entity classification service : PASS")


if __name__ == "__main__":
    run()