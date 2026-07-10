from app.prompts.editorial.archetype_rules import ARCHETYPE_RULES
from app.prompts.editorial.category_mapper import get_archetype
from app.prompts.editorial.common_rules import COMMON_RULES
from app.prompts.editorial.fact_rules import FACT_RULES
from app.prompts.editorial.language_rules import LANGUAGE_RULES
from app.prompts.editorial.style_examples import STYLE_EXAMPLES


def build_editorial_prompt(
    topic: str,
    category: str,
    evidence_text: str,
) -> str:
    archetype = get_archetype(category)
    archetype_rules = ARCHETYPE_RULES.get(
        archetype,
        ARCHETYPE_RULES["GENERAL"],
    )

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

Evidence:
{evidence_text}

Before writing the final answer, internally verify:
- The answer is only in Kannada.
- There are no mixed-script words.
- There are no broken Kannada words.
- The tone is neutral, clear and non-dramatic.
- The article follows the selected archetype structure.
- No unsupported facts are added.
- The answer reads like a Kannada encyclopedia or school reference book.

Return only the final Kannada article.
"""
