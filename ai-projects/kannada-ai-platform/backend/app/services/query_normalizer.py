QUERY_MAP = {
    "who is kuvempu": "ಕುವೆಂಪು ಯಾರು?",
    "kuvempu yaru": "ಕುವೆಂಪು ಯಾರು?",
    "tell me about bengaluru": "ಬೆಂಗಳೂರು ಬಗ್ಗೆ ಹೇಳಿ",
    "namaskara meaning": "ನಮಸ್ಕಾರ ಎಂದರೇನು?"
}


def normalize_question(question: str) -> str:
    cleaned = question.strip().lower()

    if cleaned in QUERY_MAP:
        return QUERY_MAP[cleaned]

    return question.strip()
