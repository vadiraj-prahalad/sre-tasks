"""
Editorial Output Profiles
=========================

Output profiles define how editorial content should be presented.

They do not control:
- factual policy;
- Kannada language quality;
- evidence validation;
- archetype-specific content;
- provider selection.

Those responsibilities remain in their existing modules.
"""

OUTPUT_PROFILE_CONCISE_ANSWER = "CONCISE_ANSWER"
OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE = "ENCYCLOPEDIA_ARTICLE"


OUTPUT_PROFILE_RULES = {
    OUTPUT_PROFILE_CONCISE_ANSWER: """
## Output Profile — Concise Answer

Create a short Kannada encyclopedia answer.

Requirements:
- Write 3–5 complete sentences.
- Use plain paragraphs.
- Do not add headings.
- Do not use Markdown.
- Do not include URLs or provider names.
- Return only the final Kannada answer.
""",

    OUTPUT_PROFILE_ENCYCLOPEDIA_ARTICLE: """
## Output Profile — Encyclopedia Article

Create a structured Kannada encyclopedia article for human editorial review.

Use this Markdown structure:

# <Kannada title>

## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

Write a clear introductory summary in 2–3 sentences.

## ಮುಖ್ಯ ಮಾಹಿತಿ

Present the most important verified facts in concise bullet points.
Include only facts supported by the supplied evidence.

## ವಿವರವಾದ ಮಾಹಿತಿ

Write 2–4 short, logically ordered paragraphs.
Follow the selected editorial archetype.
Each paragraph must focus on one main idea.

## ಮಹತ್ವ

Explain the historical, literary, cultural, scientific, geographical,
social or educational importance of the topic when supported by evidence.

Output requirements:
- Kannada only, except unavoidable proper names.
- Use natural, publication-quality Kannada.
- Use Markdown headings exactly as shown.
- Do not include provider names or raw URLs inside the article.
- Do not invent missing details.
- Omit sections or statements that cannot be supported by evidence.
- Do not include analysis, reasoning, or instructions.
- Return only the final Kannada article.
""",
}


def get_output_profile_rules(
    output_profile: str,
) -> str:
    """
    Return the requested output-format contract.

    Unknown profiles safely fall back to the existing concise format.
    """

    normalized_profile = (
        output_profile
        or OUTPUT_PROFILE_CONCISE_ANSWER
    ).strip().upper()

    return OUTPUT_PROFILE_RULES.get(
        normalized_profile,
        OUTPUT_PROFILE_RULES[
            OUTPUT_PROFILE_CONCISE_ANSWER
        ],
    )
