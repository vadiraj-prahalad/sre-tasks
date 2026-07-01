import json
from pathlib import Path


ALIASES_PATH = Path(__file__).resolve().parent.parent / "data" / "aliases.json"


def load_aliases() -> dict:
    if not ALIASES_PATH.exists():
        return {}

    with open(ALIASES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def resolve_alias(question: str) -> str | None:
    aliases = load_aliases()
    cleaned_question = question.strip().lower()

    return aliases.get(cleaned_question)
