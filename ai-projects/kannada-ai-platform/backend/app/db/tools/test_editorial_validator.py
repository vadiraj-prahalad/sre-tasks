"""
Editorial Validator Test
========================

Validates the deterministic quality gate used before CMS draft storage.
"""

from app.services.editorial_validator_service import (
    validate_editorial_article,
)


VALID_ARTICLE = """
# ಕುವೆಂಪು

## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

ಕುವೆಂಪು ಕನ್ನಡದ ಪ್ರಮುಖ ಕವಿ, ನಾಟಕಕಾರ ಮತ್ತು ಚಿಂತಕರಾಗಿದ್ದರು.
ಅವರ ಪೂರ್ಣ ಹೆಸರು ಕುಪ್ಪಳ್ಳಿ ವೆಂಕಟಪ್ಪ ಪುಟ್ಟಪ್ಪ.

## ಮುಖ್ಯ ಮಾಹಿತಿ

- ಕುವೆಂಪು ಅವರ ಕಾವ್ಯನಾಮ.
- ಅವರು ಜ್ಞಾನಪೀಠ ಪ್ರಶಸ್ತಿ ಪಡೆದ ಮೊದಲ ಕನ್ನಡ ಲೇಖಕರಾಗಿದ್ದರು.
- ಅವರನ್ನು ರಸಋಷಿ ಎಂದು ಕರೆಯಲಾಗುತ್ತದೆ.

## ಮಹತ್ವ

ಕುವೆಂಪು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದ ಲೇಖಕರಾಗಿದ್ದರು.
ವಿವಿಧ ಸಾಹಿತ್ಯ ಪ್ರಕಾರಗಳಲ್ಲಿ ನೀಡಿದ ಕೊಡುಗೆಯಿಂದ ಕನ್ನಡ ಸಾಹಿತ್ಯ
ಇತಿಹಾಸದಲ್ಲಿ ಅವರಿಗೆ ವಿಶೇಷ ಸ್ಥಾನವಿದೆ.
""".strip()


DUPLICATE_ARTICLE = """
# ಕುವೆಂಪು

## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

ಕುವೆಂಪು ಕನ್ನಡದ ಪ್ರಮುಖ ಕವಿಯಾಗಿದ್ದರು.

## ಮುಖ್ಯ ಮಾಹಿತಿ

- ಅವರು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದರು.
- ಅವರು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದರು.

## ಮಹತ್ವ

ಕನ್ನಡ ಸಾಹಿತ್ಯ ಇತಿಹಾಸದಲ್ಲಿ ಅವರಿಗೆ ವಿಶೇಷ ಸ್ಥಾನವಿದೆ.
ಕನ್ನಡ ಸಾಹಿತ್ಯ ಇತಿಹಾಸದಲ್ಲಿ ಅವರಿಗೆ ವಿಶೇಷ ಸ್ಥಾನವಿದೆ.
""".strip()


MISSING_SECTION_ARTICLE = """
# ಕುವೆಂಪು

## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

ಕುವೆಂಪು ಕನ್ನಡದ ಪ್ರಮುಖ ಕವಿಯಾಗಿದ್ದರು.
""".strip()


PLACEHOLDER_ARTICLE = """
# ಕುವೆಂಪು

## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

AI ಕನ್ನಡ ಕರಡು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.

## ಮುಖ್ಯ ಮಾಹಿತಿ

- ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.

## ಮಹತ್ವ

ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.
""".strip()


def run() -> None:
    valid_result = validate_editorial_article(
        VALID_ARTICLE
    )

    assert valid_result["valid"] is True, (
        valid_result["errors"]
    )

    assert (
        0.0
        <= valid_result["metrics"]["kannada_ratio"]
        <= 1.0
    ), (
        "Kannada ratio must remain between 0 and 1."
    )

    duplicate_result = (
        validate_editorial_article(
            DUPLICATE_ARTICLE
        )
    )

    assert duplicate_result["valid"] is False
    assert duplicate_result[
        "metrics"
    ]["duplicate_block_count"] > 0

    missing_section_result = (
        validate_editorial_article(
            MISSING_SECTION_ARTICLE
        )
    )

    assert missing_section_result["valid"] is False

    placeholder_result = (
        validate_editorial_article(
            PLACEHOLDER_ARTICLE
        )
    )

    assert placeholder_result["valid"] is False

    english_article_result = (
        validate_editorial_article(
            """
# Kuvempu

## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

Kuvempu was an Indian poet and writer.

## ಮುಖ್ಯ ಮಾಹಿತಿ

- He was a Kannada writer.

## ಮಹತ್ವ

He made important contributions to literature.
"""
        )
    )

    assert english_article_result["valid"] is False

    print("=" * 72)
    print("Editorial Validator Test")
    print("=" * 72)
    print("Valid Kannada article         : PASS")
    print("Kannada ratio validation      : PASS")
    print("Duplicate block detection     : PASS")
    print("Missing section detection     : PASS")
    print("Placeholder detection         : PASS")
    print("English leakage detection     : PASS")
    print("=" * 72)
    print("Editorial validator service   : PASS")


if __name__ == "__main__":
    run()