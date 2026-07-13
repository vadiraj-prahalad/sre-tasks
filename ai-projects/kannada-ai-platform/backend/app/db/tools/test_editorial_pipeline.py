"""
Editorial Pipeline Integration Test
===================================

Purpose
-------
Validate the complete editorial acquisition pipeline without using:

- Internet
- LLM
- database writes

This test protects the Canonical Knowledge Model architecture and
verifies that structured Wikidata P31 metadata survives the evidence
pipeline.

Pipeline
--------
resolve_entity()
        ↓
collect_topic_evidence()      (mock)
        ↓
build_evidence()
        ↓
analyze_evidence_conflicts()
        ↓
enrich_entity()
        ↓
generate_editorial_draft()    (mock)
        ↓
save_draft_answer()           (mock)

Phase 6.1 expectation
---------------------
Wikidata instance_of_ids must survive evidence normalization.

Entity classification is not implemented in this increment, so:

    entity_type == "GENERAL"
"""

from unittest.mock import patch

from app.services.internet_knowledge_service import (
    import_topic_as_draft,
)


MOCK_EVIDENCE = [
    {
        "provider": "English Wikipedia",
        "trust_level": "medium",
        "status": "success",
        "title": "Kempe Gowda I",
        "summary": (
            "Founder of Bengaluru."
        ),
        "url": (
            "https://example.com/wiki"
        ),
        "metadata": {
            "wikibase_item": "Q6387049",
            "english_label": (
                "Kempe Gowda I"
            ),
            "kannada_label": (
                "ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ"
            ),
            "english_aliases": [
                "Kempegowda",
                "Magadi Kempegowda",
            ],
            "kannada_aliases": [
                "ಕೆಂಪೇಗೌಡ",
                "ಮಾಗಡಿ ಕೆಂಪೇಗೌಡ",
            ],
        },
    },
    {
        "provider": "Wikidata",
        "trust_level": "high",
        "status": "success",
        "title": "Kempe Gowda I",
        "summary": (
            "Founder of Bengaluru."
        ),
        "url": (
            "https://www.wikidata.org/"
            "wiki/Q6387049"
        ),
        "entity_id": "Q6387049",
        "metadata": {
            "lookup_method": (
                "exact_entity_id"
            ),
            "entity_id": "Q6387049",
            "english_label": (
                "Kempe Gowda I"
            ),
            "kannada_label": (
                "ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ"
            ),
            "english_aliases": [
                "Kempegowda",
                "Magadi Kempegowda",
            ],
            "kannada_aliases": [
                "ಕೆಂಪೇಗೌಡ",
                "ಮಾಗಡಿ ಕೆಂಪೇಗೌಡ",
            ],
            "instance_of_ids": [
                "Q5",
            ],
        },
    },
]


def run() -> None:
    """
    Execute the integration test with all external boundaries mocked.
    """

    with (
        patch(
            (
                "app.services."
                "internet_knowledge_service."
                "collect_topic_evidence"
            ),
            return_value=MOCK_EVIDENCE,
        ),
        patch(
            (
                "app.services."
                "internet_knowledge_service."
                "generate_editorial_draft"
            ),
            return_value=(
                "ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ ಬೆಂಗಳೂರು "
                "ನಗರದ ಸಂಸ್ಥಾಪಕರಾಗಿದ್ದರು."
            ),
        ),
        patch(
            (
                "app.services."
                "internet_knowledge_service."
                "save_draft_answer"
            ),
            return_value={
                "status": "saved",
                "draft_id": 101,
                "hit_count": 1,
            },
        ),
    ):
        result = import_topic_as_draft(
            "Kempegowda",
            "history",
        )

    assert result["status"] == (
        "draft_created"
    )
    assert result["wikidata_id"] == (
        "Q6387049"
    )
    assert result["entity_type"] == (
        "PERSON"
    )
    assert result[
        "blocking_conflict"
    ] is False

    wikidata_source = next(
        source
        for source in result["sources"]
        if source["provider"]
        == "Wikidata"
    )

    assert wikidata_source[
        "instance_of_ids"
    ] == ["Q5"]

    print("=" * 72)
    print(
        "Editorial Pipeline Integration Test"
    )
    print("=" * 72)

    important_fields = [
        "status",
        "topic",
        "resolved_topic",
        "canonical_name_en",
        "canonical_name_kn",
        "display_name",
        "entity_type",
        "wikidata_id",
        "entity_confidence",
        "resolution_method",
        "successful_sources",
        "blocking_conflict",
    ]

    for field in important_fields:
        print(
            f"{field:22}: "
            f"{result.get(field)}"
        )

    print("-" * 72)
    print(
        "Wikidata P31 IDs     : "
        f"{wikidata_source['instance_of_ids']}"
    )
    print(
        "Expected entity type : PERSON"
    )
    print("-" * 72)
    print("Draft:")
    print(result["draft"])
    print("=" * 72)
    print(
        "Editorial pipeline integration: PASS"
    )


if __name__ == "__main__":
    run()