from typing import Any

import requests


class WikidataProvider:
    name = "Wikidata"

    # Wikidata itself is reliable, but free-text search results
    # must still be validated before use.
    trust_level = "medium"

    API_URL = "https://www.wikidata.org/w/api.php"

    def _request(self, params: dict[str, Any]) -> requests.Response:
        return requests.get(
            self.API_URL,
            timeout=15,
            headers={
                "User-Agent": "KannadaAIPlatform/0.1 (learning project)"
            },
            params=params,
        )

    def fetch(self, topic: str) -> dict[str, Any]:
        """
        Fallback free-text entity search.

        Prefer fetch_by_id() whenever Wikipedia provides a wikibase_item.
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
                "message": f"Wikidata request failed: {error}",
            }

        if response.status_code != 200:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.API_URL,
                "message": f"Wikidata returned {response.status_code}",
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
                "message": "Wikidata returned invalid JSON.",
            }

        results = data.get("search", [])

        if not results:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.API_URL,
                "message": "No Wikidata entity found.",
            }

        # This remains only a fallback candidate.
        entity = results[0]

        entity_id = entity.get("id")
        label = entity.get("label", topic)
        description = entity.get("description", "")

        return {
            "provider": self.name,
            "trust_level": self.trust_level,
            "status": "success",
            "topic": topic,
            "title": label,
            "summary": description,
            "entity_id": entity_id,
            "url": f"https://www.wikidata.org/wiki/{entity_id}",
            "metadata": {
                "lookup_method": "text_search",
                "entity_id": entity_id,
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
        Fetch an exact Wikidata entity using a Q-ID supplied by Wikipedia.

        Example:
            fetch_by_id("Q771686", "Basava")
        """

        normalized_id = (entity_id or "").strip().upper()

        if not normalized_id.startswith("Q"):
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "invalid",
                "topic": topic,
                "entity_id": normalized_id,
                "url": self.API_URL,
                "message": "Invalid Wikidata entity ID.",
            }

        try:
            response = self._request(
                {
                    "action": "wbgetentities",
                    "ids": normalized_id,
                    "props": "labels|descriptions|aliases",
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
                "url": f"https://www.wikidata.org/wiki/{normalized_id}",
                "message": f"Wikidata request failed: {error}",
            }

        if response.status_code != 200:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "entity_id": normalized_id,
                "url": f"https://www.wikidata.org/wiki/{normalized_id}",
                "message": f"Wikidata returned {response.status_code}",
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
                "url": f"https://www.wikidata.org/wiki/{normalized_id}",
                "message": "Wikidata returned invalid JSON.",
            }

        entity = data.get("entities", {}).get(normalized_id, {})

        if not entity or entity.get("missing") is not None:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "entity_id": normalized_id,
                "url": f"https://www.wikidata.org/wiki/{normalized_id}",
                "message": "Exact Wikidata entity was not found.",
            }

        labels = entity.get("labels", {})
        descriptions = entity.get("descriptions", {})
        aliases = entity.get("aliases", {})

        english_label = labels.get("en", {}).get("value")
        kannada_label = labels.get("kn", {}).get("value")

        english_description = descriptions.get("en", {}).get("value", "")
        kannada_description = descriptions.get("kn", {}).get("value", "")

        title = english_label or kannada_label or topic or normalized_id
        summary = english_description or kannada_description

        return {
            "provider": self.name,
            "trust_level": "high",
            "status": "success",
            "topic": topic,
            "title": title,
            "summary": summary,
            "entity_id": normalized_id,
            "url": f"https://www.wikidata.org/wiki/{normalized_id}",
            "metadata": {
                "lookup_method": "exact_entity_id",
                "entity_id": normalized_id,
                "english_label": english_label,
                "kannada_label": kannada_label,
                "english_description": english_description,
                "kannada_description": kannada_description,
                "english_aliases": [
                    item.get("value")
                    for item in aliases.get("en", [])
                    if item.get("value")
                ],
                "kannada_aliases": [
                    item.get("value")
                    for item in aliases.get("kn", [])
                    if item.get("value")
                ],
            },
        }