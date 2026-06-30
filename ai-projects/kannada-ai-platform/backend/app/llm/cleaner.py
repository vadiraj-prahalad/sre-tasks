import re


def clean_response(text: str) -> str:
    if not text:
        return ""

    # Remove English words for now
    text = re.sub(r"[a-zA-Z]+", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()
