PROTECTED_FACTS = [
    "ನಿತ್ಯ ಭೇದವಿದೆ",
    "ವಿಷ್ಣುವನ್ನು ಪರಮ ಸತ್ಯ",
    "ಉಡುಪಿಯ ಶ್ರೀಕೃಷ್ಣ ಮಠ",
    "ಕರ್ನಾಟಕ ಸಂಗೀತದ ಪಿತಾಮಹ",
    "ಸಾಹಸ ಸಿಂಹ",
    "ಜ್ಞಾನಪೀಠ",
    "ರಾಷ್ಟ್ರಕವಿ",
]


def compose_direct_answer(question: str, chunk_text: str, max_sentences: int = 4) -> str:
    cleaned_text = clean_text(chunk_text)
    sentences = split_sentences(cleaned_text)

    if not sentences:
        return cleaned_text

    keywords = extract_keywords(question)

    selected_indexes = set()

    # Always keep first sentence for context.
    selected_indexes.add(0)

    # Always keep protected facts if present.
    for index, sentence in enumerate(sentences):
        if contains_protected_fact(sentence):
            selected_indexes.add(index)

    scored_sentences = []

    for index, sentence in enumerate(sentences):
        score = score_sentence(sentence, keywords)

        scored_sentences.append(
            {
                "index": index,
                "sentence": sentence,
                "score": score,
            }
        )

    ranked_sentences = sorted(
        scored_sentences,
        key=lambda item: (-item["score"], item["index"]),
    )

    for item in ranked_sentences:
        if item["score"] <= 0:
            continue

        selected_indexes.add(item["index"])

        if len(selected_indexes) >= max_sentences:
            break

    if len(selected_indexes) < min(2, len(sentences)):
        selected_indexes.add(1)

    selected_sentences = [
        sentences[index]
        for index in sorted(selected_indexes)
    ]

    return " ".join(selected_sentences[:max_sentences])


def clean_text(text: str) -> str:
    cleaned = text.replace("#", "")
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def split_sentences(text: str) -> list[str]:
    sentences = []
    current = ""

    for character in text:
        current += character

        if character in [".", "।", "?", "!"]:
            sentence = current.strip()
            if sentence:
                sentences.append(sentence)
            current = ""

    if current.strip():
        sentences.append(current.strip())

    return sentences


def extract_keywords(question: str) -> list[str]:
    stop_words = {
        "ಯಾರು",
        "ಏನು",
        "ಎಂದರೇನು",
        "ಹೇಳಿ",
        "ವಿವರಿಸಿ",
        "ಸಂಬಂಧ",
        "ಜೊತೆ",
        "ಮತ್ತು",
        "ಬಗ್ಗೆ",
        "the",
        "what",
        "who",
        "is",
    }

    words = [
        word.strip()
        for word in question.split()
        if len(word.strip()) >= 3
    ]

    keywords = [
        word for word in words
        if word not in stop_words
    ]

    if "ಕೊಡುಗೆ" in question:
        keywords.extend(["ಸರಳಿ", "ಜಂಟಿ", "ಅಲಂಕಾರ", "ಗೀತೆ"])

    return keywords

def score_sentence(sentence: str, keywords: list[str]) -> int:
    score = 0

    for keyword in keywords:
        if keyword in sentence:
            score += 2

    if contains_protected_fact(sentence):
        score += 3

    return score


def contains_protected_fact(sentence: str) -> bool:
    for fact in PROTECTED_FACTS:
        if fact in sentence:
            return True

    return False
