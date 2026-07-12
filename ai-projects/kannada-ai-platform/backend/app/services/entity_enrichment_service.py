from dataclasses import replace
from typing import Any

from app.models.knowledge_entity import KnowledgeEntity


def _clean_text(value: Any) -> str:
    """
    Convert a string value into normalized text.

    Non-string and empty values become an empty string.
    """

    if not isinstance(value, str):
        return ""

    return " ".join(value.strip().split())


def _unique_values(values: list[Any]) -> tuple[str, ...]:
    """
    Normalize and deduplicate values while preserving their order.
    """

    unique_values: list[str] = []
    seen_values: set[str] = set()

    for value in values:
        cleaned_value = _clean_text(value)

        if not cleaned_value:
            continue

        comparison_key = cleaned_value.casefold()

        if comparison_key in seen_values:
            continue

        seen_values.add(comparison_key)
        unique_values.append(cleaned_value)

    return tuple(unique_values)


def _find_source(
    sources: list[dict[str, Any]],
    provider_name: str,
) -> dict[str, Any] | None:
    """
    Return the first normalized source from the requested provider.
    """

    for source in sources:
        if source.get("provider") == provider_name:
            return source

    return None


def _build_resolution_method(
    current_method: str,
    enrichment_found: bool,
) -> str:
    """
    Add provider enrichment to the resolution method only once.
    """

    clean_method = _clean_text(current_method) or "unresolved"

    if not enrichment_found:
        return clean_method

    method_parts = [
        part.strip()
        for part in clean_method.split("+")
        if part.strip()
    ]

    if "provider_evidence" not in method_parts:
        method_parts.append("provider_evidence")

    return "+".join(method_parts)


def enrich_entity(
    entity: KnowledgeEntity,
    sources: list[dict[str, Any]],
) -> KnowledgeEntity:
    """
    Enrich a KnowledgeEntity using normalized, conflict-safe evidence.

    Source priorities:

    Canonical English name:
    1. English Wikipedia title
    2. Wikidata English label
    3. Existing entity value

    Canonical Kannada name:
    1. Kannada Wikipedia title
    2. Wikidata Kannada label
    3. Existing entity value

    Wikidata identity:
    1. Wikidata entity ID
    2. English Wikipedia Wikibase item
    3. Kannada Wikipedia Wikibase item
    4. Existing entity value

    Aliases:
    - Wikidata English and Kannada aliases
    - Existing entity aliases

    Internal resolved topic:
    - Canonical English name when available
    - Existing resolved topic otherwise

    Display name:
    - Canonical Kannada name when available
    - Existing display name
    - Canonical English name
    - Resolved topic

    This service does not:
    - call external providers;
    - parse user questions;
    - classify entity type;
    - detect evidence conflicts;
    - generate prompts or answers;
    - save drafts or articles;
    - modify the supplied evidence.

    KnowledgeEntity is immutable, so a new instance is returned.
    """

    english_wikipedia = (
        _find_source(sources, "English Wikipedia") or {}
    )
    kannada_wikipedia = (
        _find_source(sources, "Kannada Wikipedia") or {}
    )
    wikidata = (
        _find_source(sources, "Wikidata") or {}
    )

    english_metadata = (
        english_wikipedia.get("metadata") or {}
    )
    kannada_metadata = (
        kannada_wikipedia.get("metadata") or {}
    )
    wikidata_metadata = (
        wikidata.get("metadata") or {}
    )

    canonical_name_en = (
        _clean_text(english_wikipedia.get("title"))
        or _clean_text(
            wikidata_metadata.get("english_label")
        )
        or entity.canonical_name_en
    )

    canonical_name_kn = (
        _clean_text(kannada_wikipedia.get("title"))
        or _clean_text(
            wikidata_metadata.get("kannada_label")
        )
        or entity.canonical_name_kn
    )

    wikidata_id = (
        _clean_text(
            wikidata_metadata.get("entity_id")
        )
        or _clean_text(
            english_metadata.get("wikibase_item")
        )
        or _clean_text(
            kannada_metadata.get("wikibase_item")
        )
        or entity.wikidata_id
    )

    english_alias_values = (
        wikidata_metadata.get("english_aliases") or []
    )
    kannada_alias_values = (
        wikidata_metadata.get("kannada_aliases") or []
    )

    if not isinstance(english_alias_values, list):
        english_alias_values = []

    if not isinstance(kannada_alias_values, list):
        kannada_alias_values = []

    aliases_en = _unique_values(
        [
            *entity.aliases_en,
            *english_alias_values,
        ]
    )

    aliases_kn = _unique_values(
        [
            *entity.aliases_kn,
            *kannada_alias_values,
        ]
    )

    resolved_topic = (
        canonical_name_en
        or entity.resolved_topic
        or entity.normalized_query
        or entity.original_query
    )

    display_name = (
        canonical_name_kn
        or entity.display_name
        or canonical_name_en
        or resolved_topic
    )

    enrichment_found = any(
        [
            canonical_name_en,
            canonical_name_kn,
            wikidata_id,
            aliases_en,
            aliases_kn,
        ]
    )

    confidence = (
        max(entity.confidence, 0.90)
        if enrichment_found
        else entity.confidence
    )

    resolution_method = _build_resolution_method(
        current_method=entity.resolution_method,
        enrichment_found=enrichment_found,
    )

    return replace(
        entity,
        resolved_topic=resolved_topic,
        canonical_name_en=canonical_name_en,
        canonical_name_kn=canonical_name_kn,
        display_name=display_name,
        wikidata_id=wikidata_id or None,
        aliases_en=aliases_en,
        aliases_kn=aliases_kn,
        confidence=confidence,
        resolution_method=resolution_method,
    )