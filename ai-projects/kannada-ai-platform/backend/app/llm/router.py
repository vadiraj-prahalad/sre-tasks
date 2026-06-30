from app.llm.local_llm import get_llm_response
from app.llm.cleaner import clean_response
from app.services.knowledge_service import find_known_answer
from app.services.query_normalizer import normalize_question


def route_llm(prompt: str) -> str:
    normalized_question = normalize_question(prompt)

    known_answer = find_known_answer(normalized_question)

    if known_answer:
        return known_answer

    response = get_llm_response(normalized_question)
    response = clean_response(response)

    return response
