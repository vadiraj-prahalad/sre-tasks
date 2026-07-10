from typing import Any


def build_evidence(
    provider_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "provider": provider_result.get("provider"),
        "trust_level": provider_result.get("trust_level", "unknown"),
        "title": provider_result.get("title"),
        "summary": provider_result.get("summary"),
        "url": provider_result.get("url"),
        "metadata": provider_result.get("metadata", {}),
    }