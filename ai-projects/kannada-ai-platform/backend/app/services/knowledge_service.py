from app.services.knowledge_repository import find_answer_by_key
from app.services.knowledge_repository import load_all_facts


KNOWN_SOURCE_TEXT = "\n\nಮೂಲ: Curated Internal Knowledge"


def add_known_source(answer: str) -> str:
    if "ಮೂಲ:" in answer:
        return answer

    return f"{answer}{KNOWN_SOURCE_TEXT}"


def find_known_answer(question: str) -> str | None:
    facts = load_all_facts()
    question = question.strip().lower()

    if question in facts:
        return add_known_source(facts[question])

    if "ನಮಸ್ಕಾರ" in question and (
        "ಅರ್ಥ" in question
        or "ಎಂದರೇನು" in question
        or "meaning" in question
        or "mean" in question
    ):
        return add_known_source(facts["ನಮಸ್ಕಾರ ಎಂದರೇನು?"])

    return None


def find_known_answer_by_key(canonical_key: str) -> str | None:
    answer = find_answer_by_key(canonical_key)

    if not answer:
        return None

    return add_known_source(answer)