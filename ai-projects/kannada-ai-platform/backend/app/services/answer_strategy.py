DIRECT_ANSWER_KEYWORDS = [
    "ಯಾರು",
    "ಏನು",
    "ಎಂದರೇನು",
    "ಸಂಬಂಧ",
    "ಹೇಳಿ",
    "ತತ್ವ",
    "ಭಕ್ತಿ",
    "ವೇದಾಂತ",
    "ಯಾವುದು",
    "ಎಲ್ಲಿ",
    "ಯಾವ",
    "who",
    "what",
    "meaning",
    "ಕೊಡುಗೆ",
]

LLM_REASONING_KEYWORDS = [
    "ಹೇಗೆ",
    "ಏಕೆ",
    "ಯಾಕೆ",
    "ವಿಶ್ಲೇಷಿಸಿ",
    "ಹೋಲಿಸಿ",
    "compare",
    "difference",
    "why",
    "how",
]


def should_use_direct_answer(question: str) -> bool:
    question = question.strip().lower()

    # Explicit reasoning questions should always use LLM
    for keyword in LLM_REASONING_KEYWORDS:
        if keyword in question:
            return False

    # Explicit factual questions should use direct answer
    for keyword in DIRECT_ANSWER_KEYWORDS:
        if keyword in question:
            return True

    # Short search-style queries (2-4 words) should also use direct answer
    words = question.split()

    if 1 <= len(words) <= 4:
        return True

    # Everything else goes to LLM
    return False