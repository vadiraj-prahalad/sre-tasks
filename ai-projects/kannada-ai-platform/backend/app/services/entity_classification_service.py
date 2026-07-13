from dataclasses import replace
from typing import Any

from app.models.knowledge_entity import KnowledgeEntity


# ------------------------------------------------------------------
# Canonical platform entity types
# ------------------------------------------------------------------

ENTITY_TYPE_GENERAL = "GENERAL"
ENTITY_TYPE_PERSON = "PERSON"


# ------------------------------------------------------------------
# Trusted Wikidata type mappings
# ------------------------------------------------------------------

# Q5 = human
#
# This is intentionally a small Beta v1 mapping.
# Additional mappings should be added only with verified ontology
# evidence and focused tests.
WIKIDATA_INSTANCE_OF_TYPE_MAP: dict[str, str] = {
    "Q5": ENTITY_TYPE_PERSON,
}


def _normalize_entity_ids(
    values: Any,
) -> tuple[str, ...]:
    """
    Normalize and deduplicate Wikidata entity IDs.

    Only valid Q-IDs are retained.

    Examples:
        ["Q5", "q5"] -> ("Q5",)
        None -> ()
        "Q5" -> ()
    """

    if not isinstance(values, list):
        return ()

    normalized_ids: list[str] = []
    seen_ids: set[str] = set()

    for value in values:
        if not isinstance(value, str):
            continue

        normalized_id = value.strip().upper()

        if (
            not normalized_id.startswith("Q")
            or not normalized_id[1:].isdigit()
        ):
            continue

        if normalized_id in seen_ids:
            continue

        seen_ids.add(normalized_id)
        normalized_ids.append(normalized_id)

    return tuple(normalized_ids)


def _collect_instance_of_ids(
    sources: list[dict[str, Any]],
) -> tuple[str, ...]:
    """
    Collect normalized Wikidata P31 IDs from accepted evidence.

    Classification consumes only evidence that has already passed
    source selection, normalization, and conflict analysis.
    """

    collected_ids: list[str] = []
    seen_ids: set[str] = set()

    for source in sources:
        if not isinstance(source, dict):
            continue

        metadata = source.get("metadata") or {}

        if not isinstance(metadata, dict):
            continue

        instance_of_ids = _normalize_entity_ids(
            metadata.get("instance_of_ids")
        )

        for entity_id in instance_of_ids:
            if entity_id in seen_ids:
                continue

            seen_ids.add(entity_id)
            collected_ids.append(entity_id)

    return tuple(collected_ids)


def determine_entity_type(
    sources: list[dict[str, Any]],
) -> str:
    """
    Determine the platform entity type from trusted provider metadata.

    Classification order:
    1. Collect normalized Wikidata P31 IDs.
    2. Apply deterministic mappings.
    3. Return GENERAL when no trusted mapping exists.

    This function does not:
    - call external providers;
    - inspect unstructured descriptions;
    - use an LLM;
    - mutate evidence;
    - modify a KnowledgeEntity.
    """

    instance_of_ids = _collect_instance_of_ids(
        sources
    )

    for instance_of_id in instance_of_ids:
        mapped_type = (
            WIKIDATA_INSTANCE_OF_TYPE_MAP.get(
                instance_of_id
            )
        )

        if mapped_type:
            return mapped_type

    return ENTITY_TYPE_GENERAL


def classify_entity(
    entity: KnowledgeEntity,
    sources: list[dict[str, Any]],
) -> KnowledgeEntity:
    """
    Return a classified immutable KnowledgeEntity.

    Existing non-GENERAL classifications are preserved. This prevents
    a lower-information classification pass from overwriting a type
    assigned by a future higher-confidence mechanism.

    During Beta v1, only deterministic Wikidata P31 mappings are used.
    """

    current_type = (
        entity.entity_type or ENTITY_TYPE_GENERAL
    ).strip().upper()

    if current_type != ENTITY_TYPE_GENERAL:
        return entity

    classified_type = determine_entity_type(
        sources
    )

    if classified_type == current_type:
        return entity

    return replace(
        entity,
        entity_type=classified_type,
    )
