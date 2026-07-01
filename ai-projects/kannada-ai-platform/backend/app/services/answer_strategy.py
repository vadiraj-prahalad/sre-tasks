DIRECT_ANSWER_KEYWORDS = [
    "ಯಾರು",
    "ಎಂದರೇನು",
    "ಏನು",
    "ಸಂಬಂಧ",
    "ಹೇಳಿ",
    "ತತ್ವ",
    "ಭಕ್ತಿ",
    "ವೇದಾಂತ",
    "who",
    "what",
    "meaning",
]


LLM_REASONING_KEYWORDS = [
    "ಹೇಗೆ",
    "ಏಕೆ",
    "ವಿಶ್ಲೇಷಿಸಿ",
    "compare",
    "why",
    "how",
]


def should_use_direct_answer(question: str) -> bool:
    question_lower = question.lower()

    for keyword in DIRECT_ANSWER_KEYWORDS:
        if keyword in question_lower:
            return True

    for keyword in LLM_REASONING_KEYWORDS:
        if keyword in question_lower:
            return False

    return False