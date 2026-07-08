from typing import Any

from app.services.draft_knowledge_service import save_draft_answer
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


def build_source_summary(sources: list[dict[str, Any]]) -> str:
    lines = []

    for index, source in enumerate(sources, start=1):
        lines.append(
            "\n".join(
                [
                    f"{index}. Provider: {source.get('provider')}",
                    f"   Trust: {source.get('trust_level')}",
                    f"   Title: {source.get('title')}",
                    f"   Summary: {source.get('summary')}",
                    f"   URL: {source.get('url')}",
                ]
            )
        )

    return "\n\n".join(lines)


def build_kannada_draft_answer(
    topic: str,
    category: str,
    sources: list[dict[str, Any]],
) -> str:
    source_summary = build_source_summary(sources)

    return (
        "ಈ ಲೇಖನವನ್ನು ಹಲವು ಇಂಟರ್ನೆಟ್ ಮೂಲಗಳ ಆಧಾರದ ಮೇಲೆ ಕರಡು ರೂಪದಲ್ಲಿ ಸಿದ್ಧಪಡಿಸಲಾಗಿದೆ.\n\n"
        f"ವಿಷಯ: {topic}\n\n"
        f"ವರ್ಗ: {category}\n\n"
        "ಸಂಗ್ರಹಿಸಿದ ಮೂಲಗಳು:\n\n"
        f"{source_summary}\n\n"
        "ಗಮನಿಸಿ:\n"
        "1. ಈ ಕರಡು ಇನ್ನೂ ಪರಿಶೀಲಿತ ಉತ್ತರವಲ್ಲ.\n"
        "2. ಮೂಲಗಳನ್ನು ಹೋಲಿಸಿ ಕನ್ನಡದಲ್ಲಿ ಸರಳ, ನಿಖರ ಮತ್ತು ಪರಿಶೀಲಿತ ಉತ್ತರವಾಗಿ ಮರುಬರೆಯಬೇಕು.\n"
        "3. ಭಿನ್ನ ಮಾಹಿತಿ ಕಂಡುಬಂದರೆ ಮಾನವ ಪರಿಶೀಲನೆ ಅಗತ್ಯ."
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
    answer = build_kannada_draft_answer(
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