from typing import Any

import requests


class WikidataProvider:
    """
    Retrieve canonical identity and structured metadata from Wikidata.

    The provider is responsible only for fetching and normalizing
    provider data. It must not convert Wikidata concepts into
    platform-specific entity classifications.
    """

    name = "Wikidata"

    # Wikidata itself is reliable, but free-text search results
    # must still be validated before use.
    trust_level = "medium"

    API_URL = "https://www.wikidata.org/w/api.php"

    def _request(
        self,
        params: dict[str, Any],
    ) -> requests.Response:
        """
        Execute a Wikidata API request with the platform User-Agent.
        """

        return requests.get(
            self.API_URL,
            timeout=15,
            headers={
                "User-Agent": (
                    "KannadaAIPlatform/0.1 "
                    "(learning project)"
                )
            },
            params=params,
        )

    @staticmethod
    def _extract_entity_ids_from_claims(
        claims: dict[str, Any],
        property_id: str,
    ) -> list[str]:
        """
        Extract unique Wikidata entity IDs from one claim property.

        Example:
            P31 -> ["Q5"]

        Only valid item-valued claims are retained.

        Missing values, malformed claims, duplicate values,
        non-item values, and invalid IDs are ignored safely.
        """

        if not isinstance(claims, dict):
            return []

        normalized_property_id = (
            property_id or ""
        ).strip().upper()

        if not normalized_property_id:
            return []

        property_claims = claims.get(
            normalized_property_id,
            [],
        )

        if not isinstance(property_claims, list):
            return []

        entity_ids: list[str] = []
        seen_ids: set[str] = set()

        for claim in property_claims:
            if not isinstance(claim, dict):
                continue

            mainsnak = claim.get("mainsnak") or {}

            if not isinstance(mainsnak, dict):
                continue

            datavalue = mainsnak.get("datavalue") or {}

            if not isinstance(datavalue, dict):
                continue

            value = datavalue.get("value") or {}

            if not isinstance(value, dict):
                continue

            entity_id = value.get("id")

            if not isinstance(entity_id, str):
                continue

            normalized_id = entity_id.strip().upper()

            if not normalized_id.startswith("Q"):
                continue

            if not normalized_id[1:].isdigit():
                continue

            if normalized_id in seen_ids:
                continue

            seen_ids.add(normalized_id)
            entity_ids.append(normalized_id)

        return entity_ids

    def fetch(
        self,
        topic: str,
    ) -> dict[str, Any]:
        """
        Perform fallback free-text entity search.

        Prefer fetch_by_id() whenever Wikipedia provides a
        canonical wikibase_item.

        Free-text search returns only a candidate. It does not provide
        trusted structured claims such as P31 and must be validated by
        the evidence-quality and conflict-analysis stages.
        """

        try:
            response = self._request(
                {
                    "action": "wbsearchentities",
                    "search": topic,
                    "language": "en",
                    "format": "json",
                    "limit": 5,
                }
            )
        except requests.RequestException as error:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "error",
                "topic": topic,
                "url": self.API_URL,
                "message": (
                    f"Wikidata request failed: {error}"
                ),
            }

        if response.status_code != 200:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.API_URL,
                "message": (
                    "Wikidata returned "
                    f"{response.status_code}"
                ),
            }

        try:
            data = response.json()
        except ValueError:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "error",
                "topic": topic,
                "url": self.API_URL,
                "message": (
                    "Wikidata returned invalid JSON."
                ),
            }

        results = data.get("search", [])

        if not isinstance(results, list) or not results:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.API_URL,
                "message": (
                    "No Wikidata entity found."
                ),
            }

        # This remains only a fallback candidate.
        entity = results[0]

        if not isinstance(entity, dict):
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.API_URL,
                "message": (
                    "Wikidata returned an invalid entity."
                ),
            }

        entity_id = entity.get("id")
        label = entity.get("label", topic)
        description = entity.get("description", "")

        if not isinstance(entity_id, str) or not entity_id:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.API_URL,
                "message": (
                    "Wikidata candidate has no entity ID."
                ),
            }

        normalized_id = entity_id.strip().upper()

        return {
            "provider": self.name,
            "trust_level": self.trust_level,
            "status": "success",
            "topic": topic,
            "title": label,
            "summary": description,
            "entity_id": normalized_id,
            "url": (
                "https://www.wikidata.org/wiki/"
                f"{normalized_id}"
            ),
            "metadata": {
                "lookup_method": "text_search",
                "entity_id": normalized_id,
                "label": label,
                "description": description,
                "match": entity.get("match"),
                "aliases": entity.get("aliases", []),
                "concept_uri": entity.get("concepturi"),
                "repository": entity.get("repository"),
            },
        }

    def fetch_by_id(
        self,
        entity_id: str,
        topic: str = "",
    ) -> dict[str, Any]:
        """
        Fetch an exact Wikidata entity using a Q-ID supplied by
        a trusted linked provider such as Wikipedia.

        In addition to multilingual identity metadata, this method
        retrieves structured claims and exposes P31 values as
        instance_of_ids.

        Example:
            fetch_by_id("Q771686", "Basava")
        """

        normalized_id = (
            entity_id or ""
        ).strip().upper()

        if (
            not normalized_id.startswith("Q")
            or not normalized_id[1:].isdigit()
        ):
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "invalid",
                "topic": topic,
                "entity_id": normalized_id,
                "url": self.API_URL,
                "message": (
                    "Invalid Wikidata entity ID."
                ),
            }

        try:
            response = self._request(
                {
                    "action": "wbgetentities",
                    "ids": normalized_id,
                    "props": (
                        "labels|descriptions|aliases|claims"
                    ),
                    "languages": "kn|en",
                    "languagefallback": 1,
                    "format": "json",
                }
            )
        except requests.RequestException as error:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "error",
                "topic": topic,
                "entity_id": normalized_id,
                "url": (
                    "https://www.wikidata.org/wiki/"
                    f"{normalized_id}"
                ),
                "message": (
                    f"Wikidata request failed: {error}"
                ),
            }

        if response.status_code != 200:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "entity_id": normalized_id,
                "url": (
                    "https://www.wikidata.org/wiki/"
                    f"{normalized_id}"
                ),
                "message": (
                    "Wikidata returned "
                    f"{response.status_code}"
                ),
            }

        try:
            data = response.json()
        except ValueError:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "error",
                "topic": topic,
                "entity_id": normalized_id,
                "url": (
                    "https://www.wikidata.org/wiki/"
                    f"{normalized_id}"
                ),
                "message": (
                    "Wikidata returned invalid JSON."
                ),
            }

        entities = data.get("entities", {})

        if not isinstance(entities, dict):
            entities = {}

        entity = entities.get(normalized_id, {})

        if (
            not isinstance(entity, dict)
            or not entity
            or entity.get("missing") is not None
        ):
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "entity_id": normalized_id,
                "url": (
                    "https://www.wikidata.org/wiki/"
                    f"{normalized_id}"
                ),
                "message": (
                    "Exact Wikidata entity was not found."
                ),
            }

        labels = entity.get("labels", {})
        descriptions = entity.get("descriptions", {})
        aliases = entity.get("aliases", {})
        claims = entity.get("claims", {})

        if not isinstance(labels, dict):
            labels = {}

        if not isinstance(descriptions, dict):
            descriptions = {}

        if not isinstance(aliases, dict):
            aliases = {}

        if not isinstance(claims, dict):
            claims = {}

        instance_of_ids = (
            self._extract_entity_ids_from_claims(
                claims=claims,
                property_id="P31",
            )
        )

        english_label = (
            labels.get("en", {}).get("value")
        )
        kannada_label = (
            labels.get("kn", {}).get("value")
        )

        english_description = (
            descriptions.get("en", {}).get(
                "value",
                "",
            )
        )
        kannada_description = (
            descriptions.get("kn", {}).get(
                "value",
                "",
            )
        )

        title = (
            english_label
            or kannada_label
            or topic
            or normalized_id
        )

        summary = (
            english_description
            or kannada_description
        )

        english_aliases = aliases.get("en", [])
        kannada_aliases = aliases.get("kn", [])

        if not isinstance(english_aliases, list):
            english_aliases = []

        if not isinstance(kannada_aliases, list):
            kannada_aliases = []

        return {
            "provider": self.name,
            "trust_level": "high",
            "status": "success",
            "topic": topic,
            "title": title,
            "summary": summary,
            "entity_id": normalized_id,
            "url": (
                "https://www.wikidata.org/wiki/"
                f"{normalized_id}"
            ),
            "metadata": {
                "lookup_method": "exact_entity_id",
                "entity_id": normalized_id,
                "english_label": english_label,
                "kannada_label": kannada_label,
                "english_description": (
                    english_description
                ),
                "kannada_description": (
                    kannada_description
                ),
                "english_aliases": [
                    item.get("value")
                    for item in english_aliases
                    if (
                        isinstance(item, dict)
                        and item.get("value")
                    )
                ],
                "kannada_aliases": [
                    item.get("value")
                    for item in kannada_aliases
                    if (
                        isinstance(item, dict)
                        and item.get("value")
                    )
                ],
                "instance_of_ids": instance_of_ids,
            },
        }