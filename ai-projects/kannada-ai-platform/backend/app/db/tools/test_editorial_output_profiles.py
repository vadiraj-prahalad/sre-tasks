"""
Editorial Output Profile Test
=============================

Validates that concise answers and CMS articles receive different,
non-conflicting output contracts.
"""

from app.prompts.editorial.output_profiles import (
    OUTPUT_PROFILE_CONCISE_ANSWER,
    OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE,
)
from app.prompts.editorial.prompt_builder import (
    build_editorial_prompt,
)


def run() -> None:
    concise_prompt = build_editorial_prompt(
        topic="ಕುವೆಂಪು",
        category="person",
        evidence_text="Verified evidence.",
        output_profile=(
            OUTPUT_PROFILE_CONCISE_ANSWER
        ),
    )

    article_prompt = build_editorial_prompt(
        topic="ಕುವೆಂಪು",
        category="person",
        evidence_text="Verified evidence.",
        output_profile=(
            OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE
        ),
    )

    assert "Write 3–5 complete sentences" in concise_prompt
    assert "Do not add headings" in concise_prompt
    assert "## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ" not in concise_prompt

    assert "## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ" in article_prompt
    assert "## ಮುಖ್ಯ ಮಾಹಿತಿ" in article_prompt
    assert "## ವಿವರವಾದ ಮಾಹಿತಿ" in article_prompt
    assert "## ಮಹತ್ವ" in article_prompt
    assert "Write 3–5 complete sentences" not in article_prompt

    assert "PERSON Article Structure" in concise_prompt
    assert "PERSON Article Structure" in article_prompt

    print("=" * 72)
    print("Editorial Output Profile Test")
    print("=" * 72)
    print("Concise output contract       : PASS")
    print("Article output contract       : PASS")
    print("No profile conflict           : PASS")
    print("Shared archetype rules        : PASS")
    print("=" * 72)


if __name__ == "__main__":
    run()
