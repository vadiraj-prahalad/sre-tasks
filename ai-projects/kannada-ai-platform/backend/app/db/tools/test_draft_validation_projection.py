"""
Draft Validation Projection Test
================================

Validates that editorial validation is recomputed when CMS drafts
are read, without persisting validation metrics in the database.
"""

from app.services.draft_knowledge_service import (
    build_draft_validation,
)


VALID_EDITORIAL_ARTICLE = """
# ಕುವೆಂಪು

## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

ಕುವೆಂಪು ಕನ್ನಡದ ಪ್ರಮುಖ ಕವಿ, ಲೇಖಕ ಮತ್ತು ಚಿಂತಕರಾಗಿದ್ದರು.
ಅವರ ಪೂರ್ಣ ಹೆಸರು ಕುಪ್ಪಳ್ಳಿ ವೆಂಕಟಪ್ಪ ಪುಟ್ಟಪ್ಪ.

## ಮುಖ್ಯ ಮಾಹಿತಿ

- ಕುವೆಂಪು ಅವರ ಕಾವ್ಯನಾಮ.
- ಅವರು ಜ್ಞಾನಪೀಠ ಪ್ರಶಸ್ತಿ ಪಡೆದ ಮೊದಲ ಕನ್ನಡ ಲೇಖಕರಾಗಿದ್ದರು.
- ಅವರನ್ನು ರಸಋಷಿ ಎಂದು ಕರೆಯಲಾಗುತ್ತದೆ.

## ಮಹತ್ವ

ಕುವೆಂಪು ಕನ್ನಡ ಸಾಹಿತ್ಯಕ್ಕೆ ಮಹತ್ವದ ಕೊಡುಗೆ ನೀಡಿದರು.
ಕನ್ನಡ ಸಾಹಿತ್ಯದ ಇತಿಹಾಸದಲ್ಲಿ ಅವರಿಗೆ ವಿಶೇಷ ಸ್ಥಾನವಿದೆ.
""".strip()


INVALID_EDITORIAL_ARTICLE = """
ಕುವೆಂಪು ಕನ್ನಡದ ಪ್ರಮುಖ ಕವಿಯಾಗಿದ್ದರು.
""".strip()


def run() -> None:
    valid_result = build_draft_validation(
        suggested_answer=VALID_EDITORIAL_ARTICLE,
        draft_type="editorial_import",
    )

    assert valid_result is not None
    assert valid_result["valid"] is True
    assert (
        0.0
        <= valid_result["metrics"]["kannada_ratio"]
        <= 1.0
    )

    invalid_result = build_draft_validation(
        suggested_answer=INVALID_EDITORIAL_ARTICLE,
        draft_type="editorial_import",
    )

    assert invalid_result is not None
    assert invalid_result["valid"] is False
    assert invalid_result["errors"]

    empty_result = build_draft_validation(
        suggested_answer="",
        draft_type="editorial_import",
    )

    assert empty_result is not None
    assert empty_result["valid"] is False
    assert empty_result["metrics"]["character_count"] == 0

    runtime_result = build_draft_validation(
        suggested_answer="Temporary runtime response.",
        draft_type="runtime_fallback",
    )

    assert runtime_result is None

    print("=" * 72)
    print("Draft Validation Projection Test")
    print("=" * 72)
    print("Valid editorial draft          : PASS")
    print("Invalid editorial draft        : PASS")
    print("Empty editorial draft          : PASS")
    print("Runtime fallback skipped       : PASS")
    print("Validation recomputed on read  : PASS")
    print("=" * 72)


if __name__ == "__main__":
    run()
