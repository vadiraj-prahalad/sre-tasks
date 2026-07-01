from app.services.knowledge_service import find_known_answer
from app.services.query_normalizer import normalize_question


def route_llm(prompt: str) -> str:
    normalized_question = normalize_question(prompt)

    known_answer = find_known_answer(normalized_question)

    if known_answer:
        return known_answer

    return "ಈ ವಿಷಯದ ವಿಶ್ವಾಸಾರ್ಹ ಮಾಹಿತಿಯನ್ನು ಇನ್ನೂ ಸೇರಿಸಲಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
