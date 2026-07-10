import re
from typing import Any
from urllib.parse import quote

import requests


class WikipediaProvider:
    name = "English Wikipedia"
    trust_level = "medium"

    BASE_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

    def clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def fetch(self, topic: str) -> dict[str, Any]:
        encoded_title = quote(topic.strip().replace(" ", "_"))
        request_url = self.BASE_URL.format(title=encoded_title)

        try:
            response = requests.get(
                request_url,
                timeout=15,
                headers={
                    "User-Agent": "KannadaAIPlatform/0.1 (learning project)"
                },
            )
        except requests.RequestException as error:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "error",
                "topic": topic,
                "url": request_url,
                "message": f"Wikipedia request failed: {error}",
            }

        if response.status_code != 200:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": request_url,
                "message": f"Wikipedia returned {response.status_code}",
            }

        try:
            data = response.json()
        except ValueError:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "error",
                "topic": topic,
                "url": request_url,
                "message": "Wikipedia returned invalid JSON.",
            }

        summary = self.clean_text(data.get("extract", ""))

        if not summary:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "empty",
                "topic": topic,
                "url": request_url,
                "message": "No summary extract found.",
            }

        titles = data.get("titles") or {}

        page_url = (
            data.get("content_urls", {})
            .get("desktop", {})
            .get("page", request_url)
        )

        return {
            "provider": self.name,
            "trust_level": self.trust_level,
            "status": "success",
            "topic": topic,
            "title": data.get("title", topic),
            "summary": summary,
            "url": page_url,
            "metadata": {
                "description": data.get("description"),
                "page_type": data.get("type"),
                "coordinates": data.get("coordinates"),
                "wikibase_item": data.get("wikibase_item"),
                "canonical_title": titles.get("canonical"),
                "normalized_title": titles.get("normalized"),
                "display_title": titles.get("display"),
            },
        }
