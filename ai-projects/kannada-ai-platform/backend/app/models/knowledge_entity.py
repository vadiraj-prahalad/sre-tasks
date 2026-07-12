from dataclasses import dataclass, field


@dataclass(frozen=True)
class KnowledgeEntity:
    """
    Canonical identity of a knowledge topic.

    This model represents WHO or WHAT the topic is.

    It intentionally does NOT contain:
    - evidence
    - prompts
    - retrieval results
    - embeddings
    - generated answers
    - editorial drafts
    - provider-specific payloads

    Those belong to later stages of the knowledge pipeline.
    """

    # ------------------------------------------------------------------
    # User Query
    # ------------------------------------------------------------------

    original_query: str
    normalized_query: str
    resolved_topic: str

    # ------------------------------------------------------------------
    # Canonical Identity
    # ------------------------------------------------------------------

    canonical_name_en: str = ""
    canonical_name_kn: str = ""
    display_name: str = ""

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    entity_type: str = "GENERAL"
    domain: str = "general"

    # ------------------------------------------------------------------
    # Global Identity
    # ------------------------------------------------------------------

    wikidata_id: str | None = None

    # ------------------------------------------------------------------
    # Known Aliases
    # ------------------------------------------------------------------

    aliases_en: tuple[str, ...] = field(default_factory=tuple)
    aliases_kn: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Resolution Metadata
    # ------------------------------------------------------------------

    confidence: float = 0.0
    resolution_method: str = "unresolved"

    # ------------------------------------------------------------------
    # Derived Properties
    # ------------------------------------------------------------------

    @property
    def preferred_name(self) -> str:
        """
        Return the best available user-facing entity name.
        """

        return (
            self.display_name
            or self.canonical_name_kn
            or self.canonical_name_en
            or self.resolved_topic
            or self.normalized_query
            or self.original_query
        )

    @property
    def changed(self) -> bool:
        """
        True if the resolver changed the original query.
        """

        return self.resolved_topic != self.original_query

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Convert the immutable entity into JSON-friendly data.
        """

        return {
            "original_query": self.original_query,
            "normalized_query": self.normalized_query,
            "resolved_topic": self.resolved_topic,
            "canonical_name_en": self.canonical_name_en,
            "canonical_name_kn": self.canonical_name_kn,
            "display_name": self.display_name,
            "preferred_name": self.preferred_name,
            "changed": self.changed,
            "entity_type": self.entity_type,
            "domain": self.domain,
            "wikidata_id": self.wikidata_id,
            "aliases_en": list(self.aliases_en),
            "aliases_kn": list(self.aliases_kn),
            "confidence": self.confidence,
            "resolution_method": self.resolution_method,
        }