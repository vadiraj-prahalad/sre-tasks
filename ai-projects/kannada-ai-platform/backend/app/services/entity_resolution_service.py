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

    cleaned = value.strip()

    suffixes = [
        " ಬಗ್ಗೆ ಹೇಳಿ",
        " ಯಾರು?",
        " ಎಂದರೇನು?",
        " ಏನು?",
    ]

    for suffix in suffixes:
        cleaned = cleaned.replace(suffix, "")

    return cleaned.strip()


def resolve_entity(
    topic: str,
    category: str | None = None,
) -> KnowledgeEntity:
    """
    Resolve a user topic into a canonical KnowledgeEntity.

    Current responsibilities:
    - Trim input
    - Alias lookup
    - Basic cleanup

    Future responsibilities:
    - Wikidata enrichment
    - Canonical Kannada title
    - Entity type detection
    - Confidence scoring
    """

    original = topic.strip()

    aliases = load_aliases()

    resolved = clean_resolved_topic(
        aliases.get(original.lower(), original)
    )

    return KnowledgeEntity(
        original_query=original,
        normalized_query=original,
        resolved_topic=resolved,
        display_name=resolved,
        domain=category or "general",
        confidence=1.0 if resolved != original else 0.90,
        resolution_method="alias_lookup",
    )