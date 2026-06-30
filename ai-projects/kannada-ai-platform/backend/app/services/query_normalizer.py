QUERY_MAP = {
    "who is kuvempu": "ಕುವೆಂಪು ಯಾರು?",
    "kuvempu yaru": "ಕುವೆಂಪು ಯಾರು?",
    "tell me about bengaluru": "ಬೆಂಗಳೂರು ಬಗ್ಗೆ ಹೇಳಿ",
    "namaskara meaning": "ನಮಸ್ಕಾರ ಎಂದರೇನು?",
    "who is dr rajkumar": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
    "who is dr. rajkumar": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
    "dr rajkumar": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
    "rajkumar actor": "ಡಾ. ರಾಜ್‌ಕುಮಾರ್ ಯಾರು?",
}


def normalize_question(question: str) -> str:
    cleaned = question.strip().lower()

    if cleaned in QUERY_MAP:
        return QUERY_MAP[cleaned]

    return question.strip()
