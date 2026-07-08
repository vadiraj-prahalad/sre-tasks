from typing import Any

from app.llm.local_llm import get_llm_response
from app.services.draft_knowledge_service import (
    get_draft_answer,
    update_draft_answer,
)
from app.prompts.kannada_editorial_guidelines import KANNADA_EDITORIAL_GUIDELINES


def build_rewrite_prompt(question: str, draft_answer: str) -> str:
    return f"""
You are a senior Kannada knowledge editor.

Use the following editorial standard for every answer:

{KANNADA_EDITORIAL_GUIDELINES}

Task:
Rewrite the draft evidence into a clean Kannada answer suitable for a public Kannada knowledge assistant.

Strict rules:
1. Return only the final Kannada answer.
2. Do not include headings.
3. Do not include provider names, URLs, trust levels, or review notes.
4. Do not copy English text directly.
5. Make the answer sound natural to native Kannada speakers.
6. Prefer textbook-style Kannada.

Original question:
{question}

Draft evidence:
{draft_answer}

Final Kannada answer:
"""


def rewrite_draft_answer(draft_id: int) -> dict[str, Any]:
    draft = get_draft_answer(draft_id)

    if draft.get("status") != "found":
        return {
            "status": "not_found",
            "draft_id": draft_id,
        }

    prompt = build_rewrite_prompt(
        question=draft["question"],
        draft_answer=draft["answer"],
    )

    rewritten_answer = get_llm_response(prompt)

    if not rewritten_answer or "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು" in rewritten_answer:
        return {
            "status": "failed",
            "draft_id": draft_id,
            "message": "LLM rewrite failed.",
        }

    update_result = update_draft_answer(
        draft_id=draft_id,
        question=draft["question"],
        answer=rewritten_answer.strip(),
    )

    return {
        "status": update_result["status"],
        "draft_id": draft_id,
        "question": draft["question"],
        "rewritten_answer": rewritten_answer.strip(),
    }
