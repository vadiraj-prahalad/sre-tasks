from typing import Any

import requests


class WikidataProvider:
    name = "Wikidata"
    trust_level = "high"

    SEARCH_URL = "https://www.wikidata.org/w/api.php"

    def fetch(self, topic: str) -> dict[str, Any]:
        response = requests.get(
            self.SEARCH_URL,
            timeout=15,
            headers={
                "User-Agent": "KannadaAIPlatform/0.1 (learning project)"
            },
            params={
                "action": "wbsearchentities",
                "search": topic,
                "language": "en",
                "format": "json",
                "limit": 1,
            },
        )

        if response.status_code != 200:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.SEARCH_URL,
                "message": f"Wikidata returned {response.status_code}",
            }

        data = response.json()
        results = data.get("search", [])

        if not results:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": self.SEARCH_URL,
                "message": "No Wikidata entity found.",
            }

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
        }