"""
Editorial Pipeline Integration Test
===================================

Purpose
-------
Validate the complete editorial acquisition pipeline without using:

- Internet
- LLM
- database writes

This test protects:

- Canonical KnowledgeEntity propagation
- Wikidata P31 metadata propagation
- Deterministic entity classification
- Encyclopedia article output profile selection
- Structured article content passed to draft storage

Pipeline
--------
resolve_entity()
        ↓
collect_topic_evidence()          mock
        ↓
build_evidence()
        ↓
analyze_evidence_conflicts()
        ↓
enrich_entity()
        ↓
classify_entity()
        ↓
generate_editorial_draft()        mock
        ↓
save_draft_answer()               mock
"""

from unittest.mock import patch

from app.prompts.editorial.output_profiles import (
    OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE,
)
from app.services.internet_knowledge_service import (
    import_topic_as_draft,
)


MOCK_ARTICLE = (
    "# ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ\n\n"
    "## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ\n\n"
    "ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡರು ಬೆಂಗಳೂರು ನಗರದ ಸಂಸ್ಥಾಪಕರಾಗಿದ್ದರು.\n\n"
    "## ಮುಖ್ಯ ಮಾಹಿತಿ\n\n"
    "- ಅವರು ವಿಜಯನಗರ ಸಾಮ್ರಾಜ್ಯದ ಅಧೀನದ ಆಡಳಿತಗಾರರಾಗಿದ್ದರು.\n"
    "- ಬೆಂಗಳೂರು ನಗರದ ಅಭಿವೃದ್ಧಿಗೆ ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದರು.\n\n"
    "## ವಿವರವಾದ ಮಾಹಿತಿ\n\n"
    "ಅವರು ಬೆಂಗಳೂರು ಪ್ರದೇಶದ ಆಡಳಿತ ಮತ್ತು ನಗರ ನಿರ್ಮಾಣದಲ್ಲಿ "
    "ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದರು.\n\n"
    "## ಮಹತ್ವ\n\n"
    "ಬೆಂಗಳೂರು ನಗರದ ಇತಿಹಾಸದಲ್ಲಿ ಅವರಿಗೆ ಪ್ರಮುಖ ಸ್ಥಾನವಿದೆ."
)


MOCK_EVIDENCE = [
    {
        "provider": "English Wikipedia",
        "trust_level": "medium",
        "status": "success",
        "title": "Kempe Gowda I",
        "summary": "Founder of Bengaluru.",
        "url": "https://example.com/wiki",
        "metadata": {
            "wikibase_item": "Q6387049",
            "english_label": "Kempe Gowda I",
            "kannada_label": "ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ",
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
        "summary": "Founder of Bengaluru.",
        "url": (
            "https://www.wikidata.org/"
            "wiki/Q6387049"
        ),
        "entity_id": "Q6387049",
        "metadata": {
            "lookup_method": "exact_entity_id",
            "entity_id": "Q6387049",
            "english_label": "Kempe Gowda I",
            "kannada_label": "ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ",
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
    Execute the editorial acquisition pipeline with all external
    boundaries mocked.
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
            return_value=MOCK_ARTICLE,
        ) as mock_generate_editorial_draft,
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
        ) as mock_save_draft_answer,
    ):
        result = import_topic_as_draft(
            "Kempegowda",
            "history",
        )

    # ------------------------------------------------------------------
    # Pipeline result validation
    # ------------------------------------------------------------------

    assert result["status"] == "draft_created"

    assert result["wikidata_id"] == "Q6387049"

    assert result["entity_type"] == "PERSON"

    assert result["blocking_conflict"] is False

    assert result["successful_sources"] == 2

    # ------------------------------------------------------------------
    # Wikidata P31 propagation validation
    # ------------------------------------------------------------------

    wikidata_source = next(
        source
        for source in result["sources"]
        if source["provider"] == "Wikidata"
    )

    assert wikidata_source[
        "instance_of_ids"
    ] == ["Q5"]

    # ------------------------------------------------------------------
    # Editorial output-profile validation
    # ------------------------------------------------------------------

    mock_generate_editorial_draft.assert_called_once()

    generate_call = (
        mock_generate_editorial_draft.call_args
    )

    assert generate_call.kwargs[
        "output_profile"
    ] == OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE, (
        "CMS imports must request the encyclopedia article profile."
    )

    assert generate_call.kwargs[
        "topic"
    ] == "ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ"

    assert generate_call.kwargs[
        "category"
    ] == "history"

    # ------------------------------------------------------------------
    # Draft-storage input validation
    # ------------------------------------------------------------------

    mock_save_draft_answer.assert_called_once()

    save_call = mock_save_draft_answer.call_args

    saved_suggested_answer = (
        save_call.kwargs.get(
            "suggested_answer",
            "",
        )
    )

    saved_evidence = (
        save_call.kwargs.get(
            "evidence",
            "",
        )
    )

    saved_category = (
        save_call.kwargs.get(
            "category",
            "",
        )
    )

    saved_draft_type = (
        save_call.kwargs.get(
            "draft_type",
            "",
        )
    )

    assert saved_suggested_answer == MOCK_ARTICLE

    assert "# ಮೊದಲನೆಯ ಕೆಂಪೇಗೌಡ" in (
        saved_suggested_answer
    )

    assert "## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ" in (
        saved_suggested_answer
    )

    assert "## ಮುಖ್ಯ ಮಾಹಿತಿ" in (
        saved_suggested_answer
    )

    assert "## ವಿವರವಾದ ಮಾಹಿತಿ" in (
        saved_suggested_answer
    )

    assert "## ಮಹತ್ವ" in (
        saved_suggested_answer
    )

    assert saved_evidence, (
        "Normalized evidence must be passed to draft storage."
    )

    assert saved_category == "history"

    assert saved_draft_type == (
        "editorial_import"
    )

    # ------------------------------------------------------------------
    # Test report
    # ------------------------------------------------------------------

    print("=" * 72)
    print("Editorial Pipeline Integration Test")
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
    print(
        "Output profile       : "
        "ENCYCLOPEDIA_ARTICLE"
    )
    print("-" * 72)
    print("Stored article sections:")
    print("- Kannada title       : PASS")
    print("- ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ       : PASS")
    print("- ಮುಖ್ಯ ಮಾಹಿತಿ          : PASS")
    print("- ವಿವರವಾದ ಮಾಹಿತಿ        : PASS")
    print("- ಮಹತ್ವ                 : PASS")
    print("- Evidence             : PASS")
    print("- Category             : PASS")
    print("- Draft type           : PASS")
    print("-" * 72)
    print("Draft save result:")
    print(result["draft"])
    print("=" * 72)
    print(
        "Editorial pipeline integration: PASS"
    )


if __name__ == "__main__":
    run()