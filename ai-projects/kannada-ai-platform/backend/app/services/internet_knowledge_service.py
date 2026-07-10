from typing import Any

from app.services.draft_knowledge_service import save_draft_answer
from app.services.editorial_draft_service import generate_editorial_draft
from app.services.entity_resolution_service import resolve_entity
from app.services.evidence_builder_service import build_evidence
from app.services.evidence_quality_service import select_clean_evidence
from app.services.internet_providers.kannada_wikipedia_provider import (
    KannadaWikipediaProvider,
)
from app.services.internet_providers.wikidata_provider import WikidataProvider
from app.services.internet_providers.wikipedia_provider import WikipediaProvider


PROVIDERS = [
    KannadaWikipediaProvider(),
    WikipediaProvider(),
    WikidataProvider(),
]


def collect_topic_evidence(topic: str) -> list[dict[str, Any]]:
    """
    Fetch raw evidence for the resolved topic from every configured provider.
    """

    evidence = []

    for provider in PROVIDERS:
        result = provider.fetch(topic)
        evidence.append(result)

    return evidence


def successful_sources(
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Keep only providers that returned usable results.
    """

    return [
        item
        for item in evidence
        if item.get("status") == "success"
    ]


def build_kannada_draft_question(topic: str) -> str:
    """
    Build the question shown in the admin draft-review queue.
    """

    return f"{topic} ಬಗ್ಗೆ ಹೇಳಿ"


def build_evidence_text(
    sources: list[dict[str, Any]],
) -> str:
    """
    Convert normalized evidence into text for the editorial prompt
    and the admin review screen.
    """

    sections = []

    for index, source in enumerate(sources, start=1):
        metadata = source.get("metadata") or {}

        lines = [
            f"{index}. Provider: {source.get('provider', 'Unknown')}",
            f"Trust: {source.get('trust_level', 'unknown')}",
            f"Title: {source.get('title', '')}",
            f"Summary: {source.get('summary', '')}",
            f"URL: {source.get('url', '')}",
        ]

        if metadata:
            lines.append(f"Metadata: {metadata}")

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def build_review_draft_answer(
    topic: str,
    category: str,
    sources: list[dict[str, Any]],
) -> str:
    """
    Generate the Kannada editorial draft and combine it with
    the supporting evidence for human review.
    """

    evidence_text = build_evidence_text(sources)

    generated_draft = generate_editorial_draft(
        topic=topic,
        category=category,
        evidence_text=evidence_text,
    )

    if not generated_draft:
        generated_draft = (
            "AI ಕನ್ನಡ ಕರಡು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. "
            "ದಯವಿಟ್ಟು ಕೆಳಗಿನ ಮೂಲಗಳ ಆಧಾರದ ಮೇಲೆ "
            "ಮಾನವ ಪರಿಶೀಲಿತ ಉತ್ತರವನ್ನು ಬರೆಯಿರಿ."
        )

    return (
        "AI ಕನ್ನಡ ಕರಡು:\n\n"
        f"{generated_draft}\n\n"
        "ಸಂಗ್ರಹಿಸಿದ ಮೂಲಗಳು:\n\n"
        f"{evidence_text}\n\n"
        "ಗಮನಿಸಿ:\n"
        "1. ಈ ಕರಡು ಇನ್ನೂ ಪರಿಶೀಲಿತ ಉತ್ತರವಲ್ಲ.\n"
        "2. ಮಾನವ ಪರಿಶೀಲನೆಯ ನಂತರ ಮಾತ್ರ ಪ್ರಕಟಿಸಬೇಕು.\n"
        "3. ತಪ್ಪು ಅಥವಾ ಅಸಹಜ ಕನ್ನಡ ಕಂಡುಬಂದರೆ ಸಂಪಾದಿಸಿ ಪ್ರಕಟಿಸಬೇಕು."
    )


def import_topic_as_draft(
    topic: str,
    category: str = "general",
) -> dict[str, Any]:
    """
    Full knowledge-acquisition flow:

    1. Resolve the input into a canonical entity.
    2. Collect evidence from configured providers.
    3. Keep successful provider responses.
    4. Reject ambiguous, irrelevant, or conflicting evidence.
    5. Normalize accepted evidence into a common format.
    6. Generate a Kannada editorial draft.
    7. Save the result in the admin draft queue.
    """

    entity = resolve_entity(topic, category)
    resolved_topic = entity["resolved"]

    raw_evidence = collect_topic_evidence(resolved_topic)

    successful_evidence = successful_sources(raw_evidence)

    clean_sources = select_clean_evidence(
        resolved_topic,
        successful_evidence,
    )

    sources = [
        build_evidence(source)
        for source in clean_sources
    ]

    if not sources:
        return {
            "status": "not_found",
            "topic": topic,
            "original_topic": topic,
            "resolved_topic": resolved_topic,
            "category": category,
            "evidence": raw_evidence,
            "message": "No relevant and trustworthy sources found.",
        }

    best_title = sources[0].get("title") or resolved_topic

    question = build_kannada_draft_question(best_title)

    answer = build_review_draft_answer(
        topic=best_title,
        category=category,
        sources=sources,
    )

    draft_result = save_draft_answer(
        question,
        answer,
    )

    return {
        "status": "draft_created",
        "topic": best_title,
        "original_topic": topic,
        "resolved_topic": resolved_topic,
        "entity_changed": entity.get("changed", False),
        "question": question,
        "category": category,
        "successful_sources": len(sources),
        "total_sources_checked": len(raw_evidence),
        "sources": [
            {
                "provider": source.get("provider"),
                "trust_level": source.get("trust_level"),
                "title": source.get("title"),
                "url": source.get("url"),
            }
            for source in sources
        ],
        "draft": draft_result,
    }