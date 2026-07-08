import re
from typing import Any
from urllib.parse import quote

import requests


class KannadaWikipediaProvider:
    name = "Kannada Wikipedia"
    trust_level = "medium"

    BASE_URL = "https://kn.wikipedia.org/api/rest_v1/page/summary/{title}"

    def clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def fetch(self, topic: str) -> dict[str, Any]:
        encoded_title = quote(topic.strip().replace(" ", "_"))
        url = self.BASE_URL.format(title=encoded_title)

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "KannadaAIPlatform/0.1 (learning project)"
            },
        )

        if response.status_code != 200:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "not_found",
                "topic": topic,
                "url": url,
                "message": f"Kannada Wikipedia returned {response.status_code}",
            }

        data = response.json()
        summary = self.clean_text(data.get("extract", ""))

        if not summary:
            return {
                "provider": self.name,
                "trust_level": self.trust_level,
                "status": "empty",
                "topic": topic,
                "url": url,
                "message": "No summary extract found.",
            }

        return {
            "provider": self.name,
            "trust_level": self.trust_level,
            "status": "success",
            "topic": topic,
            "title": data.get("title", topic),
            "summary": summary,
            "url": data.get("content_urls", {})
            .get("desktop", {})
            .get("page", url),
        }
