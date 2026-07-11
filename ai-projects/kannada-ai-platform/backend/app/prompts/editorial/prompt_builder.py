from app.prompts.editorial.archetype_rules import ARCHETYPE_RULES
from app.prompts.editorial.category_mapper import get_archetype
from app.prompts.editorial.common_rules import COMMON_RULES
from app.prompts.editorial.editorial_evaluation import EDITORIAL_CHECKLIST
from app.prompts.editorial.fact_rules import FACT_RULES
from app.prompts.editorial.language_rules import LANGUAGE_RULES
from app.prompts.editorial.style_examples import STYLE_EXAMPLES


def build_editorial_prompt(
    topic: str,
    category: str,
    evidence_text: str,
    conflict_instructions: str = "",
) -> str:
    archetype = get_archetype(category)
    archetype_rules = ARCHETYPE_RULES.get(
        archetype,
        ARCHETYPE_RULES["GENERAL"],
    )

    warning_text = conflict_instructions.strip() or "ಯಾವುದೇ ಎಚ್ಚರಿಕೆಗಳಿಲ್ಲ."

    return f"""
You are a senior Kannada encyclopedia editor.

Use the following editorial policy.

{COMMON_RULES}

{LANGUAGE_RULES}

{FACT_RULES}

{STYLE_EXAMPLES}

{archetype_rules}

Task:
Create a clean Kannada draft article from the evidence below.

Topic:
{topic}

Category:
{category}

Editorial Archetype:
{archetype}

Evidence warnings:
{warning_text}

Rules for evidence warnings:
- If years conflict, omit uncertain dates.
- If entity IDs conflict, do not generate an article.
- If belief wording is detected, preserve cautious wording.
- Do not choose one disputed value merely because one source has higher trust.
- Prefer omission over publishing an unresolved contradiction.

Evidence:
{evidence_text}

Before writing the final answer, internally verify:

{EDITORIAL_CHECKLIST}

Return only the final Kannada article.
"""