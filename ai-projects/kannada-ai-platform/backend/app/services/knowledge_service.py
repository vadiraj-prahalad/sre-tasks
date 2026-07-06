from app.services.knowledge_repository import find_answer_by_key
from app.services.knowledge_repository import load_all_facts


KNOWN_SOURCE_TEXT = "\n\nಮೂಲ: Curated Internal Knowledge"


def add_known_source(answer: str) -> str:
    if "ಮೂಲ:" in answer:
        return answer

    return f"{answer}{KNOWN_SOURCE_TEXT}"


def normalize_lookup_text(text: str) -> str:
    return (
        text.strip()
        .lower()
        .replace("ಡಾ.", "ಡಾ")
        .replace("್ ", " ")
        .replace("್", "")
    )


def find_known_answer(question: str) -> str | None:
    facts = load_all_facts()
    normalized_question = normalize_lookup_text(question)

    normalized_facts = {
        normalize_lookup_text(key): value
        for key, value in facts.items()
    }

    if normalized_question in normalized_facts:
        return add_known_source(normalized_facts[normalized_question])

    if "ನಮಸ್ಕಾರ" in normalized_question and (
        "ಅರ್ಥ" in normalized_question
        or "ಎಂದರೇನು" in normalized_question
        or "meaning" in normalized_question
        or "mean" in normalized_question
    ):
        return add_known_source(normalized_facts["ನಮಸ್ಕಾರ ಎಂದರೇನು?"])

    return None


def find_known_answer_by_key(canonical_key: str) -> str | None:
    answer = find_answer_by_key(canonical_key)

    if answer:
        return add_known_source(answer)

    return find_known_answer(canonical_key)