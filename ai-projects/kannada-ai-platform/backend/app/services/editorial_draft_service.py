from app.llm.local_llm import get_llm_response
from app.prompts.kannada_editorial_guidelines import KANNADA_EDITORIAL_GUIDELINES


def build_editorial_prompt(topic: str, category: str, evidence_text: str) -> str:
    return f"""
You are a Kannada textbook editor.

Use this editorial standard:

{KANNADA_EDITORIAL_GUIDELINES}

Task:
Create a clean Kannada draft article from the evidence below.

Rules:
1. Write only in Kannada.
2. Preserve meaning and facts from evidence.
3. Do not invent unsupported facts.
4. Use native-speaker Kannada.
5. Use textbook-style language.
6. Keep it 3 to 5 sentences.
7. Do not include URLs, provider names, or headings.
8. If evidence is limited, write cautiously.

Topic:
{topic}

Category:
{category}

Evidence:
{evidence_text}

Kannada draft:
"""


def generate_editorial_draft(topic: str, category: str, evidence_text: str) -> str:
    prompt = build_editorial_prompt(topic, category, evidence_text)
    result = get_llm_response(prompt)

    if not result or "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು" in result:
        return ""

    return result.strip()
