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

    This helper is retained for future structured date validation.
    It is not used for Beta v1 conflict detection because multiple
    years may represent different valid facts.
    """

    normalized = normalize_digits(value)

    return {
        int(match)
        for match in YEAR_PATTERN.findall(normalized)
    }


def source_text(source: dict[str, Any]) -> str:
    """
    Combine useful textual fields from one normalized evidence source.
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
    Detect folklore, tradition, or belief wording.
    """

    normalized = (value or "").casefold()

    return any(
        phrase.casefold() in normalized
        for phrase in BELIEF_PHRASES
    )


def clean_metadata(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Retain only metadata useful to editorial generation and entity handling.

    Raw API matches, HTML display values, repositories, and other
    provider-specific implementation details are removed.
    """

    if not metadata:
        return {}

    cleaned: dict[str, Any] = {}

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
    Detect multiple years in evidence.

    Important:
    This detector is intentionally not called in Beta v1.

    Multiple years do not necessarily conflict. They may represent:
    - birth and death years;
    - founding and completion years;
    - reign periods;
    - multiple valid historical events.

    It should be re-enabled only after evidence includes structured
    date roles such as birth_year, death_year, or founded_year.
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
                "Do not include uncertain dates unless their roles are clear."
            ),
        }
    ]


def detect_entity_id_conflicts(
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Detect whether accepted sources refer to different Wikidata entities.
    """

    entity_ids: dict[str, list[str]] = {}

    for source in sources:
        provider = source.get("provider", "Unknown")
        metadata = source.get("metadata") or {}

        entity_id = (
            metadata.get("wikibase_item")
            or metadata.get("entity_id")
            or source.get("entity_id")
        )

        if not entity_id:
            continue

        normalized_id = str(entity_id).strip().upper()

        if not normalized_id:
            continue

        entity_ids.setdefault(
            normalized_id,
            [],
        ).append(provider)

    if len(entity_ids) <= 1:
        return []

    return [
        {
            "type": "entity_id_conflict",
            "entity_ids": entity_ids,
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

    providers: list[str] = []

    for source in sources:
        if not contains_belief_language(source_text(source)):
            continue

        provider = source.get("provider", "Unknown")

        if provider not in providers:
            providers.append(provider)

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
    Analyze accepted evidence before editorial generation.

    Beta v1 behavior:
    - clean provider metadata;
    - detect conflicting entity IDs;
    - detect belief or tradition wording;
    - do not infer year conflicts from unstructured text.

    Returns cleaned sources and editorial warnings.
    """

    cleaned_sources: list[dict[str, Any]] = []

    for source in sources:
        cleaned_source = {
            **source,
            "metadata": clean_metadata(
                source.get("metadata") or {}
            ),
        }
        cleaned_sources.append(cleaned_source)

    warnings: list[dict[str, Any]] = []

    warnings.extend(
        detect_entity_id_conflicts(cleaned_sources)
    )

    # Year conflict detection is disabled for Beta v1.
    #
    # Multiple years may represent different valid facts, such as
    # birth year, death year, founding year, or reign period.
    #
    # Re-enable only after evidence contains structured date roles.
    #
    # warnings.extend(
    #     detect_year_conflicts(cleaned_sources)
    # )

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
    Convert conflict warnings into concise editorial instructions.
    """

    if not warnings:
        return ""

    lines = [
        "Editorial evidence warnings:",
    ]

    for index, warning in enumerate(warnings, start=1):
        instruction = str(
            warning.get("instruction", "")
        ).strip()

        if instruction:
            lines.append(f"{index}. {instruction}")

    return "\n".join(lines)