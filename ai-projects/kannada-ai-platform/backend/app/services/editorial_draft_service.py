from app.prompts.editorial.prompt_builder import build_editorial_prompt
from app.services.ai_editor_provider import generate_editorial_text


def generate_editorial_draft(
    topic: str,
    category: str,
    evidence_text: str,
    conflict_instructions: str = "",
) -> str:
    prompt = build_editorial_prompt(
        topic=topic,
        category=category,
        evidence_text=evidence_text,
        conflict_instructions=conflict_instructions,
    )

    result = generate_editorial_text(prompt)

    if not result or "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು" in result:
        return ""

    return result.strip()