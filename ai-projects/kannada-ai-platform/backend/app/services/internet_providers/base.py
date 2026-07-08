from typing import Any, Protocol


class InternetKnowledgeProvider(Protocol):
    name: str
    trust_level: str

    def fetch(self, topic: str) -> dict[str, Any]:
        ...
