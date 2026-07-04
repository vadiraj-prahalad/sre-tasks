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

    exact_match = aliases.get(cleaned_question)

    if exact_match:
        return exact_match

    for alias, key in aliases.items():
        if alias in cleaned_question:
            return key

    return None
