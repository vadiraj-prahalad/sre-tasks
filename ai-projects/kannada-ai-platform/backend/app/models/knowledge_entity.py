from dataclasses import dataclass, field


@dataclass(frozen=True)
class KnowledgeEntity:
    """
    Canonical identity of a topic in the knowledge platform.

    This model describes what the topic is. It must not contain
    evidence, prompts, drafts, embeddings, or retrieval results.
    """

    original_query: str
    normalized_query: str
    resolved_topic: str

    canonical_name_en: str = ""
    canonical_name_kn: str = ""
    display_name: str = ""

    entity_type: str = "GENERAL"
    domain: str = "general"

    wikidata_id: str | None = None

    aliases_en: tuple[str, ...] = field(default_factory=tuple)
    aliases_kn: tuple[str, ...] = field(default_factory=tuple)

    confidence: float = 0.0
    resolution_method: str = "unresolved"

    @property
    def preferred_name(self) -> str:
        """
        Return the best available user-facing name.
        """

        return (
            self.display_name
            or self.canonical_name_kn
            or self.canonical_name_en
            or self.resolved_topic
            or self.normalized_query
            or self.original_query
        )

    def to_dict(self) -> dict:
        """
        Convert the immutable model into JSON-friendly data.
        """

        return {
            "original_query": self.original_query,
            "normalized_query": self.normalized_query,
            "resolved_topic": self.resolved_topic,
            "canonical_name_en": self.canonical_name_en,
            "canonical_name_kn": self.canonical_name_kn,
            "display_name": self.display_name,
            "preferred_name": self.preferred_name,
            "entity_type": self.entity_type,
            "domain": self.domain,
            "wikidata_id": self.wikidata_id,
            "aliases_en": list(self.aliases_en),
            "aliases_kn": list(self.aliases_kn),
            "confidence": self.confidence,
            "resolution_method": self.resolution_method,
        }