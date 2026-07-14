from typing import Any

from app.services.draft_knowledge_service import (
    save_draft_answer,
)
from app.services.editorial_draft_service import (
    generate_editorial_draft,
)
from app.services.entity_enrichment_service import (
    enrich_entity,
)
from app.services.entity_resolution_service import (
    resolve_entity,
)
from app.services.evidence_builder_service import (
    build_evidence,
)
from app.services.evidence_conflict_service import (
    analyze_evidence_conflicts,
    build_conflict_instructions,
)
from app.services.evidence_quality_service import (
    select_clean_evidence,
)
from app.services.internet_providers.kannada_wikipedia_provider import (
    KannadaWikipediaProvider,
)
from app.services.internet_providers.wikidata_provider import (
    WikidataProvider,
)
from app.services.internet_providers.wikipedia_provider import (
    WikipediaProvider,
)
from app.services.entity_classification_service import (
    classify_entity,
)
from app.prompts.editorial.output_profiles import (
    OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE,
)


def collect_topic_evidence(
    topic: str,
) -> list[dict[str, Any]]:
    """
    Collect evidence in a controlled order.

    Flow:
    1. Try Kannada Wikipedia.
    2. Resolve the topic through English Wikipedia.
    3. If Wikipedia supplies a Wikidata Q-ID, fetch that exact entity.
    4. Use fuzzy Wikidata search only as a fallback.

    Exact Wikidata retrieval also exposes structured P31
    instance-of IDs for the later entity-classification stage.
    """

    evidence: list[
        dict[str, Any]
    ] = []

    kannada_result = (
        KannadaWikipediaProvider().fetch(
            topic
        )
    )
    evidence.append(
        kannada_result
    )

    wikipedia_result = (
        WikipediaProvider().fetch(
            topic
        )
    )
    evidence.append(
        wikipedia_result
    )

    wikidata_provider = (
        WikidataProvider()
    )

    wikipedia_metadata = (
        wikipedia_result.get(
            "metadata"
        )
        or {}
    )

    wikibase_item = (
        wikipedia_metadata.get(
            "wikibase_item"
        )
    )

    if (
        wikipedia_result.get("status")
        == "success"
        and wikibase_item
    ):
        wikidata_result = (
            wikidata_provider.fetch_by_id(
                entity_id=wikibase_item,
                topic=topic,
            )
        )
    else:
        wikidata_result = (
            wikidata_provider.fetch(
                topic
            )
        )

    evidence.append(
        wikidata_result
    )

    return evidence


def successful_sources(
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Retain provider responses that completed successfully.
    """

    return [
        item
        for item in evidence
        if (
            isinstance(item, dict)
            and item.get("status")
            == "success"
        )
    ]


def build_kannada_draft_question(
    topic: str,
) -> str:
    """
    Build the question displayed in the admin draft queue.
    """

    return f"{topic} ಬಗ್ಗೆ ಹೇಳಿ"


def format_metadata(
    metadata: dict[str, Any],
) -> list[str]:
    """
    Convert useful normalized evidence metadata into readable lines.

    Noisy metadata is removed by evidence_conflict_service before
    this function receives the evidence.
    """

    if not isinstance(metadata, dict) or not metadata:
        return []

    labels = {
        "description": "Description",
        "page_type": "Page type",
        "coordinates": "Coordinates",
        "wikibase_item": "Wikidata ID",
        "canonical_title": "Canonical title",
        "normalized_title": "Normalized title",
        "display_title": "Display title",
        "entity_id": "Entity ID",
        "lookup_method": "Lookup method",
        "english_label": "English label",
        "kannada_label": "Kannada label",
        "english_description": (
            "English description"
        ),
        "kannada_description": (
            "Kannada description"
        ),
        "english_aliases": "English aliases",
        "kannada_aliases": "Kannada aliases",
        "instance_of_ids": (
            "Wikidata instance-of IDs"
        ),
    }

    lines: list[str] = []

    for key, value in metadata.items():
        if value in (
            None,
            "",
            [],
            {},
        ):
            continue

        label = labels.get(
            key,
            key.replace(
                "_",
                " ",
            ).title(),
        )

        lines.append(
            f"{label}: {value}"
        )

    return lines


def build_evidence_text(
    sources: list[dict[str, Any]],
) -> str:
    """
    Convert normalized, cleaned evidence into text for:

    - the editorial prompt;
    - the admin review screen.

    Structured metadata remains visible for developer traceability.
    Entity classification itself is performed by a later service.
    """

    sections: list[str] = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        lines = [
            (
                f"{index}. Provider: "
                f"{source.get('provider', 'Unknown')}"
            ),
            (
                "Trust: "
                f"{source.get('trust_level', 'unknown')}"
            ),
            (
                "Title: "
                f"{source.get('title', '')}"
            ),
            (
                "Summary: "
                f"{source.get('summary', '')}"
            ),
            (
                "URL: "
                f"{source.get('url', '')}"
            ),
        ]

        metadata = (
            source.get("metadata") or {}
        )

        metadata_lines = (
            format_metadata(
                metadata
            )
        )

        if metadata_lines:
            lines.append(
                "Metadata:"
            )
            lines.extend(
                f"- {metadata_line}"
                for metadata_line
                in metadata_lines
            )

        sections.append(
            "\n".join(lines)
        )

    return "\n\n".join(
        sections
    )


def build_review_draft_answer(
    topic: str,
    category: str,
    sources: list[dict[str, Any]],
    conflict_instructions: str = "",
) -> dict[str, str]:
    """
    Generate structured editorial content for human review.

    The returned values keep the AI-generated Kannada answer,
    supporting evidence, editorial warnings, and the legacy
    combined review text separate.
    """

    evidence_text = (
        build_evidence_text(
            sources
        )
    )

    generated_draft = (
        generate_editorial_draft(
            topic=topic,
            category=category,
            evidence_text=evidence_text,
            conflict_instructions=(
                conflict_instructions
            ),
            output_profile=(
                OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE
            ),
        )
    )

    if not generated_draft:
        generated_draft = (
            "AI ಕನ್ನಡ ಕರಡು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. "
            "ದಯವಿಟ್ಟು ಕೆಳಗಿನ ಮೂಲಗಳ ಆಧಾರದ ಮೇಲೆ "
            "ಮಾನವ ಪರಿಶೀಲಿತ ಉತ್ತರವನ್ನು ಬರೆಯಿರಿ."
        )

    clean_conflict_instructions = (
        conflict_instructions.strip()
    )

    warning_section = ""

    if clean_conflict_instructions:
        warning_section = (
            "\n\n"
            "ಸಾಕ್ಷ್ಯ ಪರಿಶೀಲನಾ ಎಚ್ಚರಿಕೆಗಳು:\n\n"
            f"{clean_conflict_instructions}"
        )

    combined_review_text = (
        "AI ಕನ್ನಡ ಕರಡು:\n\n"
        f"{generated_draft}\n\n"
        "ಸಂಗ್ರಹಿಸಿದ ಮೂಲಗಳು:\n\n"
        f"{evidence_text}"
        f"{warning_section}\n\n"
        "ಗಮನಿಸಿ:\n"
        "1. ಈ ಕರಡು ಇನ್ನೂ ಪರಿಶೀಲಿತ ಉತ್ತರವಲ್ಲ.\n"
        "2. ಮಾನವ ಪರಿಶೀಲನೆಯ ನಂತರ ಮಾತ್ರ ಪ್ರಕಟಿಸಬೇಕು.\n"
        "3. ತಪ್ಪು ಅಥವಾ ಅಸಹಜ ಕನ್ನಡ ಕಂಡುಬಂದರೆ "
        "ಸಂಪಾದಿಸಿ ಪ್ರಕಟಿಸಬೇಕು.\n"
        "4. ಸಾಕ್ಷ್ಯಗಳಲ್ಲಿ ಭಿನ್ನ ಮಾಹಿತಿ ಇದ್ದರೆ "
        "ಪರಿಶೀಲಿಸದೆ ಪ್ರಕಟಿಸಬಾರದು."
    )

    return {
        "suggested_answer": (
            generated_draft.strip()
        ),
        "evidence": (
            evidence_text.strip()
        ),
        "editorial_warnings": (
            clean_conflict_instructions
        ),
        "combined_review_text": (
            combined_review_text
        ),
    }


def import_topic_as_draft(
    topic: str,
    category: str = "general",
) -> dict[str, Any]:
    """
    Execute the complete knowledge-acquisition pipeline.

    Flow:
    1. Resolve the original topic into a canonical entity.
    2. Collect raw evidence from providers.
    3. Retain successful provider results.
    4. Remove ambiguous or unrelated sources.
    5. Normalize accepted evidence.
    6. Clean metadata and detect evidence conflicts.
    7. Block generation when different entities are detected.
    8. Enrich the canonical entity.
    9. Generate a Kannada editorial draft.
    10. Save the draft for human approval.

    Phase 6.1 transports Wikidata instance-of IDs through this
    pipeline but intentionally leaves entity_type as GENERAL.
    """

    entity = resolve_entity(
        topic,
        category,
    )

    resolved_topic = (
        entity.resolved_topic
    )

    raw_evidence = (
        collect_topic_evidence(
            resolved_topic
        )
    )

    successful_evidence = (
        successful_sources(
            raw_evidence
        )
    )

    clean_sources = (
        select_clean_evidence(
            resolved_topic,
            successful_evidence,
        )
    )

    normalized_sources = [
        build_evidence(source)
        for source in clean_sources
    ]

    conflict_result = (
        analyze_evidence_conflicts(
            normalized_sources
        )
    )

    sources = (
        conflict_result["sources"]
    )
    warnings = (
        conflict_result["warnings"]
    )

    conflict_instructions = (
        build_conflict_instructions(
            warnings
        )
    )

    if not sources:
        return {
            "status": "not_found",
            "topic": entity.preferred_name,
            "original_topic": (
                entity.original_query
            ),
            "resolved_topic": (
                entity.resolved_topic
            ),
            "entity_changed": (
                entity.changed
            ),
            "category": (
                entity.domain
            ),
            "evidence": raw_evidence,
            "evidence_warnings": warnings,
            "message": (
                "No relevant and trustworthy "
                "sources found."
            ),
        }

    # Different entity IDs indicate that the evidence may refer
    # to different real-world entities. Do not spend editorial AI
    # resources or create a draft until this is resolved.
    if conflict_result[
        "blocking_conflict"
    ]:
        return {
            "status": "blocked_conflict",
            "topic": entity.preferred_name,
            "original_topic": (
                entity.original_query
            ),
            "resolved_topic": (
                entity.resolved_topic
            ),
            "entity_changed": (
                entity.changed
            ),
            "category": (
                entity.domain
            ),
            "successful_sources": (
                len(sources)
            ),
            "total_sources_checked": (
                len(raw_evidence)
            ),
            "evidence_warnings": warnings,
            "has_evidence_conflicts": True,
            "blocking_conflict": True,
            "message": (
                "Evidence refers to conflicting "
                "entities. Draft generation was blocked."
            ),
        }

    entity = enrich_entity(
        entity=entity,
        sources=sources,
    )

    entity = classify_entity(
        entity=entity,
        sources=sources,
    )

    best_title = (
        entity.preferred_name
    )

    question = (
        build_kannada_draft_question(
            best_title
        )
    )

    review_content = (
        build_review_draft_answer(
            topic=best_title,
            category=entity.domain,
            sources=sources,
            conflict_instructions=(
                conflict_instructions
            ),
        )
    )

    draft_result = (
        save_draft_answer(
            question,
            review_content[
                "combined_review_text"
            ],
            suggested_answer=(
                review_content[
                    "suggested_answer"
                ]
            ),
            evidence=(
                review_content[
                    "evidence"
                ]
            ),
            editorial_warnings=(
                review_content[
                    "editorial_warnings"
                ]
            ),
            category=entity.domain,
            draft_type=(
                "editorial_import"
            ),
        )
    )

    return {
        "status": "draft_created",
        "topic": best_title,
        "original_topic": (
            entity.original_query
        ),
        "resolved_topic": (
            entity.resolved_topic
        ),
        "entity_changed": (
            entity.changed
        ),

        # Canonical KnowledgeEntity fields
        "canonical_name_en": (
            entity.canonical_name_en
        ),
        "canonical_name_kn": (
            entity.canonical_name_kn
        ),
        "display_name": (
            entity.display_name
        ),
        "preferred_name": (
            entity.preferred_name
        ),
        "entity_type": (
            entity.entity_type
        ),
        "domain": (
            entity.domain
        ),
        "wikidata_id": (
            entity.wikidata_id
        ),
        "entity_confidence": (
            entity.confidence
        ),
        "resolution_method": (
            entity.resolution_method
        ),

        # Editorial pipeline metadata
        "question": question,
        "category": (
            entity.domain
        ),
        "successful_sources": (
            len(sources)
        ),
        "total_sources_checked": (
            len(raw_evidence)
        ),
        "has_evidence_conflicts": (
            conflict_result[
                "has_conflicts"
            ]
        ),
        "blocking_conflict": (
            conflict_result[
                "blocking_conflict"
            ]
        ),
        "evidence_warnings": warnings,
        "sources": [
            {
                "provider": source.get(
                    "provider"
                ),
                "trust_level": source.get(
                    "trust_level"
                ),
                "title": source.get(
                    "title"
                ),
                "url": source.get(
                    "url"
                ),
                "instance_of_ids": (
                    (
                        source.get(
                            "metadata"
                        )
                        or {}
                    ).get(
                        "instance_of_ids",
                        [],
                    )
                ),
            }
            for source in sources
        ],
        "draft": draft_result,
    }