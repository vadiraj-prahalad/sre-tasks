import json
from pathlib import Path

ALIASES_PATH = Path(__file__).resolve().parent.parent / "data" / "entity_aliases.json"


def load_aliases() -> dict:
    if not ALIASES_PATH.exists():
        return {}

    with ALIASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_entity(topic: str, category: str | None = None) -> dict:
    original = topic.strip()
    key = original.lower()

    aliases = load_aliases()
    resolved = clean_resolved_topic(aliases.get(key, original))

    return {
        "original": original,
        "resolved": resolved,
        "changed": resolved != original,
        "category": category,
    }

def clean_resolved_topic(value: str) -> str:
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