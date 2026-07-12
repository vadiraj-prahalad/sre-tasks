import json
from pathlib import Path

from app.models.knowledge_entity import KnowledgeEntity


ALIASES_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "entity_aliases.json"
)


def load_aliases() -> dict:
    if not ALIASES_PATH.exists():
        return {}

    with ALIASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def clean_resolved_topic(value: str) -> str:
    """
    Remove common Kannada question suffixes so that entity
    resolution always works on a clean topic name.
    """

    cleaned = (value or "").strip()

    suffixes = [
        " ಬಗ್ಗೆ ಹೇಳಿ",
        " ಬಗ್ಗೆ ತಿಳಿಸಿ",
        " ಯಾರು?",
        " ಯಾರು",
        " ಎಂದರೇನು?",
        " ಎಂದರೇನು",
        " ಏನು?",
        " ಏನು",
    ]

    for suffix in suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned.removesuffix(suffix).strip()

    return cleaned


def resolve_entity(
    topic: str,
    category: str | None = None,
) -> KnowledgeEntity:
    """
    Resolve a user topic into a canonical KnowledgeEntity.

    Responsibilities:
    - Clean the user query.
    - Resolve curated aliases.
    - Return a basic KnowledgeEntity.

    External enrichment (Wikipedia/Wikidata) happens later.
    """

    original_query = (topic or "").strip()

    normalized_query = clean_resolved_topic(original_query)

    aliases = load_aliases()

    alias_value = aliases.get(normalized_query.lower())
    alias_matched = alias_value is not None

    resolved_topic = clean_resolved_topic(
        alias_value if alias_matched else normalized_query
    )

    if alias_matched:
        confidence = 1.0
        resolution_method = "alias_lookup"
    elif resolved_topic:
        confidence = 0.50
        resolution_method = "normalized_input"
    else:
        confidence = 0.0
        resolution_method = "empty_input"

    return KnowledgeEntity(
        original_query=original_query,
        normalized_query=normalized_query,
        resolved_topic=resolved_topic,
        display_name=resolved_topic,
        domain=(category or "general").strip().lower(),
        confidence=confidence,
        resolution_method=resolution_method,
    )