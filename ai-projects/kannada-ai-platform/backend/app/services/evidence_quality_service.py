from typing import Any


LOW_VALUE_WIKIDATA_PHRASES = [
    "human settlement",
    "ship built",
    "family name",
    "surname",
]


DISAMBIGUATION_PHRASES = [
    "may refer to",
    "disambiguation",
]


def normalize_text(value: str) -> str:
    return (value or "").lower().replace(".", "").replace(",", "").strip()


def title_similarity(topic: str, title: str) -> float:
    topic_words = set(normalize_text(topic).split())
    title_words = set(normalize_text(title).split())

    if not topic_words or not title_words:
        return 0.0

    overlap = topic_words.intersection(title_words)
    return len(overlap) / max(len(topic_words), len(title_words))


def is_disambiguation_source(source: dict[str, Any]) -> bool:
    title = normalize_text(source.get("title", ""))
    summary = normalize_text(source.get("summary", ""))

    return any(
        phrase in title or phrase in summary
        for phrase in DISAMBIGUATION_PHRASES
    )


def is_low_value_wikidata_source(source: dict[str, Any]) -> bool:
    if source.get("provider") != "Wikidata":
        return False

    summary = normalize_text(source.get("summary", ""))

    return any(
        phrase in summary
        for phrase in LOW_VALUE_WIKIDATA_PHRASES
    )


def source_base_score(provider: str) -> int:
    if provider == "Kannada Wikipedia":
        return 100

    if provider == "English Wikipedia":
        return 95

    if provider == "Wikidata":
        return 45

    return 30


def score_source(topic: str, source: dict[str, Any]) -> float:
    provider = source.get("provider", "")
    title = source.get("title", "")

    score = source_base_score(provider)
    score += title_similarity(topic, title) * 50

    return round(score, 2)


def select_clean_evidence(
    topic: str,
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cleaned = []

    for source in sources:
        if is_disambiguation_source(source):
            continue

        if is_low_value_wikidata_source(source):
            continue

        source["resolution_score"] = score_source(topic, source)
        cleaned.append(source)

    ranked = sorted(
        cleaned,
        key=lambda item: item.get("resolution_score", 0),
        reverse=True,
    )

    if not ranked:
        return []

    best_title = ranked[0].get("title", topic)

    final_sources = []

    for source in ranked:
        provider = source.get("provider")
        title = source.get("title", "")

        if provider == "Wikidata":
            similarity_to_best = title_similarity(best_title, title)

            if similarity_to_best < 0.5:
                continue

        final_sources.append(source)

    return final_sources
