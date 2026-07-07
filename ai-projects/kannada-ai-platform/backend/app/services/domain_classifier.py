SENSITIVE_DOMAIN_KEYWORDS = {
    "religion": [
        "krishna",
        "rama",
        "shiva",
        "ganesha",
        "vishnu",
        "lakshmi",
        "hanuman",
        "bhagavad gita",
        "veda",
        "upanishad",
        "islam",
        "christianity",
        "jesus",
        "buddha",
        "ಕೃಷ್ಣ",
        "ರಾಮ",
        "ಶಿವ",
        "ಗಣೇಶ",
        "ವಿಷ್ಣು",
        "ಲಕ್ಷ್ಮಿ",
        "ಹನುಮಂತ",
        "ಭಗವದ್ಗೀತೆ",
        "ವೇದ",
        "ಉಪನಿಷತ್",
        "ಇಸ್ಲಾಂ",
        "ಕ್ರೈಸ್ತ",
        "ಯೇಸು",
        "ಬುದ್ಧ",
    ],
    "medical": [
        "pain",
        "medicine",
        "tablet",
        "doctor",
        "symptom",
        "treatment",
        "ರೋಗ",
        "ಔಷಧಿ",
        "ನೋವು",
        "ಚಿಕಿತ್ಸೆ",
        "ವೈದ್ಯ",
    ],
    "legal": [
        "law",
        "legal",
        "court",
        "case",
        "visa",
        "immigration",
        "ಕಾನೂನು",
        "ನ್ಯಾಯಾಲಯ",
        "ಕೇಸ್",
        "ವೀಸಾ",
    ],
}


STRICT_VERIFIED_ONLY_DOMAINS = {"religion", "medical", "legal"}


def classify_domain(question: str) -> str:
    cleaned_question = question.strip().lower()

    for domain, keywords in SENSITIVE_DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in cleaned_question:
                return domain

    return "general"


def requires_verified_source(question: str) -> bool:
    domain = classify_domain(question)
    return domain in STRICT_VERIFIED_ONLY_DOMAINS
