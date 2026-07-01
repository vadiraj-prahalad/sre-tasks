from app.services.knowledge_repository import load_all_facts
from app.services.knowledge_repository import find_answer_by_key


def find_known_answer(question: str) -> str | None:
    facts = load_all_facts()
    question = question.strip().lower()

    if question in facts:
        return facts[question]

    if "ನಮಸ್ಕಾರ" in question and (
        "ಅರ್ಥ" in question
        or "ಎಂದರೇನು" in question
        or "meaning" in question
        or "mean" in question
    ):
        return facts["ನಮಸ್ಕಾರ ಎಂದರೇನು?"]

    return None
def find_known_answer_by_key(canonical_key: str) -> str | None:
    return find_answer_by_key(canonical_key)
