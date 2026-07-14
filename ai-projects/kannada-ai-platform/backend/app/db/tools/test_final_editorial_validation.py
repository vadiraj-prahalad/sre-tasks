"""
Final Editorial Validation Test
===============================

Validates the publishing boundary for human-edited articles.
"""

from unittest.mock import patch

from app.services.draft_knowledge_service import (
    create_article_from_draft,
)


VALID_ARTICLE = """
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
ಕನ್ನಡ ಸಾಹಿತ್ಯ ಇತಿಹಾಸದಲ್ಲಿ ಅವರಿಗೆ ವಿಶೇಷ ಸ್ಥಾನವಿದೆ.
""".strip()


INVALID_ARTICLE = """
ಕುವೆಂಪು ಕನ್ನಡದ ಪ್ರಮುಖ ಕವಿಯಾಗಿದ್ದರು.
""".strip()


def run() -> None:
    publishing_draft = {
        "status": "found",
        "draft_status": "publishing",
    }

    with (
        patch(
            "app.services.draft_knowledge_service.get_draft_answer",
            return_value=publishing_draft,
        ),
        patch(
            "app.services.draft_knowledge_service.add_admin_article",
            return_value={
                "article": {
                    "id": 501,
                }
            },
        ) as add_article_mock,
    ):
        valid_result = (
            create_article_from_draft(
                draft_id=101,
                approved_question=(
                    "ಕುವೆಂಪು ಬಗ್ಗೆ ಹೇಳಿ"
                ),
                approved_answer=(
                    VALID_ARTICLE
                ),
                category="literature",
            )
        )

    assert valid_result["status"] == (
        "article_created"
    )

    assert valid_result[
        "validation"
    ]["valid"] is True

    add_article_mock.assert_called_once()

    with (
        patch(
            "app.services.draft_knowledge_service.get_draft_answer",
            return_value=publishing_draft,
        ),
        patch(
            "app.services.draft_knowledge_service.add_admin_article",
        ) as blocked_add_article_mock,
    ):
        invalid_result = (
            create_article_from_draft(
                draft_id=102,
                approved_question=(
                    "ಕುವೆಂಪು ಬಗ್ಗೆ ಹೇಳಿ"
                ),
                approved_answer=(
                    INVALID_ARTICLE
                ),
                category="literature",
            )
        )

    assert invalid_result["status"] == (
        "editorial_validation_failed"
    )

    assert invalid_result[
        "validation"
    ]["valid"] is False

    assert invalid_result[
        "validation"
    ]["errors"]

    blocked_add_article_mock.assert_not_called()

    print("=" * 72)
    print("Final Editorial Validation Test")
    print("=" * 72)
    print("Valid edited article published : PASS")
    print("Invalid edited article blocked : PASS")
    print("Article write prevented         : PASS")
    print("=" * 72)


if __name__ == "__main__":
    run()