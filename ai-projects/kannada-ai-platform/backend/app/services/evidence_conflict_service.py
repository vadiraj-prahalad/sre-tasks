import re
from typing import Any


YEAR_PATTERN = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")

KANNADA_DIGIT_MAP = str.maketrans(
    {
        "೦": "0",
        "೧": "1",
        "೨": "2",
        "೩": "3",
        "೪": "4",
        "೫": "5",
        "೬": "6",
        "೭": "7",
        "೮": "8",
        "೯": "9",
    }
)

BELIEF_PHRASES = [
    "traditional belief",
    "traditionally believed",
    "it is believed",
    "according to legend",
    "legend says",
    "ಸಂಪ್ರದಾಯದ ಪ್ರಕಾರ",
    "ಸಂಪ್ರದಾಯದ ನಂಬಿಕೆಯಂತೆ",
    "ನಂಬಿಕೆಯಂತೆ",
    "ಎಂದು ನಂಬಲಾಗಿದೆ",
]

USEFUL_METADATA_FIELDS = {
    "description",
    "page_type",
    "coordinates",
    "wikibase_item",
    "canonical_title",
    "normalized_title",
    "entity_id",
    "lookup_method",
    "english_label",
    "kannada_label",
    "english_description",
    "kannada_description",
    "english_aliases",
    "kannada_aliases",
}


def normalize_digits(value: str) -> str:
    """
    Convert Kannada numerals to Arabic numerals so dates can be compared.

    Example:
        ೧೧೩೪-೧೧೯೬ -> 1134-1196
    """

    return (value or "").translate(KANNADA_DIGIT_MAP)


def extract_years(value: str) -> set[int]:
    """
    Extract four-digit years from English or Kannada text.
    """

    normalized = normalize_digits(value)

    return {
        int(match)
        for match in YEAR_PATTERN.findall(normalized)
    }


def source_text(source: dict[str, Any]) -> str:
    """
    Combine the useful textual fields of one evidence source.
    """

    metadata = source.get("metadata") or {}

    values = [
        source.get("title", ""),
        source.get("summary", ""),
        metadata.get("description", ""),
        metadata.get("english_description", ""),
        metadata.get("kannada_description", ""),
    ]

    return " ".join(
        str(value)
        for value in values
        if value
    )


def contains_belief_language(value: str) -> bool:
    """
    Detect whether a source contains folklore, tradition, or belief wording.
    """

    normalized = (value or "").lower()

    return any(
        phrase.lower() in normalized
        for phrase in BELIEF_PHRASES
    )


def clean_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Keep only metadata that is useful for editorial generation.

    This removes noisy fields such as HTML display titles, raw API matches,
    repository data, and other provider-specific implementation details.
    """

    if not metadata:
        return {}

    cleaned = {}

    for key, value in metadata.items():
        if key not in USEFUL_METADATA_FIELDS:
            continue

        if value in (None, "", [], {}):
            continue

        cleaned[key] = value

    return cleaned


def detect_year_conflicts(
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Detect differing years across accepted evidence sources.

    This is intentionally conservative. It reports possible conflicts but
    does not try to decide which source is correct.
    """

    year_sources: dict[int, list[str]] = {}

    for source in sources:
        provider = source.get("provider", "Unknown")
        years = extract_years(source_text(source))

        for year in years:
            year_sources.setdefault(year, []).append(provider)

    unique_years = sorted(year_sources)

    if len(unique_years) <= 1:
        return []

    return [
        {
            "type": "year_conflict",
            "years": unique_years,
            "sources": {
                str(year): providers
                for year, providers in year_sources.items()
            },
            "instruction": (
                "Multiple different years appear in the evidence. "
                "Do not include uncertain dates unless the sources clearly agree."
            ),
        }
    ]


def detect_entity_id_conflicts(
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Detect whether accepted sources refer to different Wikidata entities.
    """

    ids: dict[str, list[str]] = {}

    for source in sources:
        provider = source.get("provider", "Unknown")
        metadata = source.get("metadata") or {}

        entity_id = (
            metadata.get("wikibase_item")
            or metadata.get("entity_id")
            or source.get("entity_id")
        )

        if entity_id:
            ids.setdefault(str(entity_id), []).append(provider)

    if len(ids) <= 1:
        return []

    return [
        {
            "type": "entity_id_conflict",
            "entity_ids": ids,
            "instruction": (
                "The evidence appears to refer to different entities. "
                "Do not generate or publish the article until the entity is resolved."
            ),
        }
    ]


def detect_belief_warnings(
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Record sources containing traditional belief or folklore wording.
    """

    providers = []

    for source in sources:
        if contains_belief_language(source_text(source)):
            providers.append(
                source.get("provider", "Unknown")
            )

    if not providers:
        return []

    return [
        {
            "type": "belief_or_tradition",
            "providers": providers,
            "instruction": (
                "Traditional beliefs must be described cautiously. "
                "Use wording such as 'ಸಂಪ್ರದಾಯದ ಪ್ರಕಾರ' or "
                "'ನಂಬಿಕೆಯಂತೆ' and do not present the claim as verified fact."
            ),
        }
    ]


def analyze_evidence_conflicts(
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Analyze accepted evidence before it is sent to the editorial model.

    Returns cleaned evidence and editorial warnings.
    """

    cleaned_sources = []

    for source in sources:
        cleaned_source = {
            **source,
            "metadata": clean_metadata(
                source.get("metadata") or {}
            ),
        }
        cleaned_sources.append(cleaned_source)

    warnings = []

    warnings.extend(
        detect_entity_id_conflicts(cleaned_sources)
    )
    warnings.extend(
        detect_year_conflicts(cleaned_sources)
    )
    warnings.extend(
        detect_belief_warnings(cleaned_sources)
    )

    blocking_conflict = any(
        warning.get("type") == "entity_id_conflict"
        for warning in warnings
    )

    return {
        "sources": cleaned_sources,
        "warnings": warnings,
        "has_conflicts": bool(warnings),
        "blocking_conflict": blocking_conflict,
    }


def build_conflict_instructions(
    warnings: list[dict[str, Any]],
) -> str:
    """
    Convert conflict warnings into concise prompt instructions.
    """

    if not warnings:
        return ""

    lines = [
        "Editorial evidence warnings:",
    ]

    for index, warning in enumerate(warnings, start=1):
        instruction = warning.get("instruction", "")
        lines.append(f"{index}. {instruction}")

    return "\n".join(lines)
