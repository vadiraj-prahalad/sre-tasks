import re
import unicodedata


GENERIC_QUERY_WORDS = {
    "ಯಾರು",
    "ಏನು",
    "ಎಂದರೇನು",
    "ಬಗ್ಗೆ",
    "ಹೇಳಿ",
    "ಜೊತೆ",
    "ಮತ್ತು",
    "ಯಾವುದು",
    "ಹೇಗೆ",
    "ಏಕೆ",
}

KANNADA_VIRAMA = "\u0CCD"

ZERO_WIDTH_CHARACTERS = {
    "\u200B",  # Zero Width Space
    "\u200C",  # Zero Width Non-Joiner
    "\u200D",  # Zero Width Joiner
    "\uFEFF",  # Zero Width No-Break Space
}


def normalize_unicode(
    text: str,
) -> str:
    """
    Return a stable Unicode-normalized, case-folded representation.

    The function does not remove meaningful Kannada characters.
    """

    return unicodedata.normalize(
        "NFC",
        text or "",
    ).casefold()


def remove_zero_width_characters(
    text: str,
) -> str:
    """
    Remove invisible Unicode spacing and join-control characters.
    """

    normalized_text = normalize_unicode(
        text
    )

    return "".join(
        character
        for character in normalized_text
        if character
        not in ZERO_WIDTH_CHARACTERS
    )


def fold_kannada_for_matching(
    text: str,
) -> str:
    """
    Produce a conservative Kannada lexical-comparison form.

    Kannada names may contain explicit virama and zero-width characters
    that are absent from commonly typed query variants.

    This representation is intended only for matching. It must not be
    used to replace original article text, display text, or embeddings.
    """

    normalized_text = normalize_unicode(
        text
    )

    return "".join(
        character
        for character in normalized_text
        if (
            character != KANNADA_VIRAMA
            and character
            not in ZERO_WIDTH_CHARACTERS
        )
    )


def normalize_terms(
    text: str,
    *,
    remove_generic_words: bool = True,
    minimum_length: int = 3,
) -> list[str]:
    """
    Extract meaningful normalized terms for lexical matching.

    Kannada question-structure words can optionally be removed so they
    do not influence entity or document ranking.
    """

    normalized_text = normalize_unicode(
        text
    )

    normalized_text = re.sub(
        r"[^\w\u0C80-\u0CFF]+",
        " ",
        normalized_text,
    )

    terms: list[str] = []

    for raw_word in normalized_text.split():
        word = raw_word.strip()

        if len(word) < minimum_length:
            continue

        if (
            remove_generic_words
            and word in GENERIC_QUERY_WORDS
        ):
            continue

        terms.append(
            word
        )

    return terms


def canonical_search_form(
    text: str,
) -> str:
    """
    Return a reusable normalized search representation.

    This is suitable for deterministic comparison, duplicate detection,
    alias lookup, and future search indexing.
    """

    terms = normalize_terms(
        text,
        remove_generic_words=False,
        minimum_length=1,
    )

    normalized_text = " ".join(
        terms
    )

    return fold_kannada_for_matching(
        normalized_text
    )