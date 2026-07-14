from app.prompts.editorial.output_profiles import (
    OUTPUT_PROFILE_CONCISE_ANSWER,
)
from app.prompts.editorial.prompt_builder import (
    build_editorial_prompt,
)
from app.services.ai_editor_provider import (
    generate_editorial_text,
)


def generate_editorial_draft(
    topic: str,
    category: str,
    evidence_text: str,
    conflict_instructions: str = "",
    output_profile: str = OUTPUT_PROFILE_CONCISE_ANSWER,
) -> str:
    """
    Generate evidence-grounded Kannada editorial content.

    The output profile controls presentation only. Factual, language,
    archetype and evidence policies remain shared.
    """

    prompt = build_editorial_prompt(
        topic=topic,
        category=category,
        evidence_text=evidence_text,
        conflict_instructions=conflict_instructions,
        output_profile=output_profile,
    )

    result = generate_editorial_text(prompt)

    if (
        not result
        or "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು" in result
    ):
        return ""

    return result.strip()
