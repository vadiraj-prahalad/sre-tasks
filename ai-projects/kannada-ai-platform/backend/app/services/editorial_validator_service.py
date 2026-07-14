import re
from typing import Any


TITLE_PATTERN = re.compile(
    r"(?m)^#\s+(.+?)\s*$"
)

SECTION_PATTERN = re.compile(
    r"(?m)^##\s+(.+?)\s*$"
)

KANNADA_CHARACTER_PATTERN = re.compile(
    r"[\u0C80-\u0CFF]"
)

REQUIRED_INTRODUCTION_SECTION = "ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ"

OPTIONAL_CONTENT_SECTIONS = {
    "ಮುಖ್ಯ ಮಾಹಿತಿ",
    "ವಿವರವಾದ ಮಾಹಿತಿ",
    "ಮಹತ್ವ",
}

BLOCKED_TEXT_FRAGMENTS = (
    "AI ಕನ್ನಡ ಕರಡು ಸಿದ್ಧಪಡಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ",
    "ಉತ್ತರವನ್ನು ಸಿದ್ಧಪಡಿಸಲು",
    "You are a senior Kannada encyclopedia editor",
    "Output Profile",
    "Editorial Archetype",
    "Provider:",
    "Evidence warnings:",
    "OpenAI",
    "Ollama",
)


def _normalize_text(value: str) -> str:
    """
    Normalize text for comparison without changing the original article.
    """

    return " ".join(
        (value or "").strip().casefold().split()
    )


def _extract_sections(
    article: str,
) -> dict[str, str]:
    """
    Extract Markdown level-two sections from an article.

    Example:

        ## ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ

        Content

        ## ಮುಖ್ಯ ಮಾಹಿತಿ

        Content
    """

    matches = list(
        SECTION_PATTERN.finditer(article)
    )

    sections: dict[str, str] = {}

    for index, match in enumerate(matches):
        section_name = match.group(1).strip()

        content_start = match.end()

        if index + 1 < len(matches):
            content_end = matches[index + 1].start()
        else:
            content_end = len(article)

        section_content = article[
            content_start:content_end
        ].strip()

        sections[section_name] = section_content

    return sections


def _extract_content_blocks(
    article: str,
) -> list[str]:
    """
    Extract paragraphs and bullet points that contain editorial content.

    Markdown headings are ignored.
    """

    blocks: list[str] = []

    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return

        paragraph = " ".join(
            line.strip()
            for line in paragraph_lines
            if line.strip()
        ).strip()

        paragraph_lines.clear()

        if paragraph:
            blocks.append(paragraph)

    for raw_line in article.splitlines():
        line = raw_line.strip()

        if not line:
            flush_paragraph()
            continue

        if line.startswith("#"):
            flush_paragraph()
            continue

        if line.startswith("- "):
            flush_paragraph()

            bullet = line[2:].strip()

            if bullet:
                blocks.append(bullet)

            continue

        paragraph_lines.append(line)

    flush_paragraph()

    return blocks


def _find_duplicate_blocks(
    article: str,
) -> list[str]:
    """
    Detect exact duplicate paragraphs or bullet points.

    Similar ideas expressed differently are left for human review or
    future semantic evaluation. This validator remains deterministic.
    """

    duplicates: list[str] = []
    seen_blocks: set[str] = set()

    for block in _extract_content_blocks(article):
        normalized_block = _normalize_text(block)

        if len(normalized_block) < 20:
            continue

        if normalized_block in seen_blocks:
            duplicates.append(block)
            continue

        seen_blocks.add(normalized_block)

    return duplicates


def validate_editorial_article(
    article: str,
) -> dict[str, Any]:
    """
    Validate the minimum structural and editorial quality of a generated
    Kannada encyclopedia article.

    This validator does not:
    - verify historical facts;
    - compare claims against evidence;
    - call an LLM;
    - judge nuanced Kannada style;
    - modify the article.

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "metrics": dict[str, Any],
        }
    """

    clean_article = (article or "").strip()

    errors: list[str] = []
    warnings: list[str] = []

    if not clean_article:
        errors.append(
            "Generated article is empty."
        )

        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "character_count": 0,
                "section_count": 0,
                "content_section_count": 0,
                "duplicate_block_count": 0,
            },
        }

    title_match = TITLE_PATTERN.search(
        clean_article
    )

    if not title_match:
        errors.append(
            "Kannada Markdown title is missing."
        )
    else:
        title = title_match.group(1).strip()

        if not KANNADA_CHARACTER_PATTERN.search(
            title
        ):
            errors.append(
                "Article title does not contain Kannada text."
            )

    sections = _extract_sections(
        clean_article
    )

    introduction = sections.get(
        REQUIRED_INTRODUCTION_SECTION,
        "",
    ).strip()

    if not introduction:
        errors.append(
            "The ಸಂಕ್ಷಿಪ್ತ ಪರಿಚಯ section is missing or empty."
        )

    populated_content_sections = [
        section_name
        for section_name
        in OPTIONAL_CONTENT_SECTIONS
        if sections.get(
            section_name,
            "",
        ).strip()
    ]

    if len(populated_content_sections) < 2:
        errors.append(
            "At least two supported content sections must contain "
            "useful information."
        )

    for blocked_fragment in BLOCKED_TEXT_FRAGMENTS:
        if blocked_fragment.casefold() in (
            clean_article.casefold()
        ):
            errors.append(
                "Article contains internal, provider, or failure text: "
                f"{blocked_fragment}"
            )

    content_blocks = _extract_content_blocks(
        clean_article
    )

    normalized_content = " ".join(
        content_blocks
    )

    if len(normalized_content) < 250:
        errors.append(
            "Article content is too short for encyclopedia review."
        )

    kannada_character_count = len(
        KANNADA_CHARACTER_PATTERN.findall(
            normalized_content
        )
    )

    alphabetic_character_count = sum(
        character.isalpha()
        for character in normalized_content
    )

    if alphabetic_character_count:
        kannada_ratio = (
            kannada_character_count
            / alphabetic_character_count
        )
    else:
        kannada_ratio = 0.0

    if kannada_ratio < 0.60:
        errors.append(
            "Article contains insufficient Kannada content."
        )

    duplicate_blocks = _find_duplicate_blocks(
        clean_article
    )

    if duplicate_blocks:
        errors.append(
            "Article contains exact duplicate paragraphs or bullet points."
        )

    if len(populated_content_sections) == 2:
        warnings.append(
            "Article uses a reduced section set because evidence may be limited."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "character_count": len(
                clean_article
            ),
            "section_count": len(
                sections
            ),
            "content_section_count": len(
                populated_content_sections
            ),
            "content_block_count": len(
                content_blocks
            ),
            "duplicate_block_count": len(
                duplicate_blocks
            ),
            "kannada_ratio": round(
                kannada_ratio,
                3,
            ),
        },
    }
