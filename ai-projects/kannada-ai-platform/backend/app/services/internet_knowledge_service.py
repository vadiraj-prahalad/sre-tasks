from typing import Any

from app.services.draft_knowledge_service import save_draft_answer
from app.services.editorial_draft_service import generate_editorial_draft
from app.services.internet_providers.kannada_wikipedia_provider import (
    KannadaWikipediaProvider,
)
from app.services.internet_providers.wikidata_provider import WikidataProvider
from app.services.internet_providers.wikipedia_provider import WikipediaProvider


PROVIDERS = [
    WikidataProvider(),
    KannadaWikipediaProvider(),
    WikipediaProvider(),
]


def collect_topic_evidence(topic: str) -> list[dict[str, Any]]:
    evidence = []

    for provider in PROVIDERS:
        result = provider.fetch(topic)
        evidence.append(result)

    return evidence


def successful_sources(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in evidence if item.get("status") == "success"]


def build_kannada_draft_question(topic: str) -> str:
    return f"{topic} ಬಗ್ಗೆ ಹೇಳಿ"


def build_evidence_text(sources: list[dict[str, Any]]) -> str:
    lines = []

    for index, source in enumerate(sources, start=1):
        lines.append(
            "\n".join(
                [
                    f"{index}. Provider: {source.get('provider')}",
                    f"Trust: {source.get('trust_level')}",
                    f"Title: {source.get('title')}",
                    f"Summary: {source.get('summary')}",
                    f"URL: {source.get('url')}",
                ]
            )
        )

    return "\n\n".join(lines)


def build_review_draft_answer(
    topic: str,
    category: str,
    sources: list[dict[str, Any]],
) -> str:
    evidence_text = build_evidence_text(sources)

    generated_draft = generate_editorial_draft(
        topic=topic,
        category=category,
        evidence_text=evidence_text,
    )

    if not generated_draft:
        generated_draft = "AI ಕನ್ನಡ ಕರಡು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೆಳಗಿನ ಮೂಲಗಳ ಆಧಾರದ ಮೇಲೆ ಮಾನವ ಪರಿಶೀಲಿತ ಉತ್ತರವನ್ನು ಬರೆಯಿರಿ."

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


def import_topic_as_draft(topic: str, category: str = "general") -> dict[str, Any]:
    evidence = collect_topic_evidence(topic)
    sources = successful_sources(evidence)

    if not sources:
        return {
            "status": "not_found",
            "topic": topic,
            "category": category,
            "evidence": evidence,
            "message": "No successful sources found.",
        }

    best_title = sources[0].get("title", topic)
    question = build_kannada_draft_question(best_title)
    answer = build_review_draft_answer(
        topic=best_title,
        category=category,
        sources=sources,
    )

    draft_result = save_draft_answer(question, answer)

    return {
        "status": "draft_created",
        "topic": best_title,
        "question": question,
        "category": category,
        "successful_sources": len(sources),
        "total_sources_checked": len(evidence),
        "sources": [
            {
                "provider": source.get("provider"),
                "trust_level": source.get("trust_level"),
                "url": source.get("url"),
            }
            for source in sources
        ],
        "draft": draft_result,
    }