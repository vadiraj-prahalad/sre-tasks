from pathlib import Path
from typing import Any

from app.services.internet_knowledge_service import import_topic_as_draft


BACKEND_DIR = Path(__file__).resolve().parents[2]


def read_topic_file(topic_file_path: str) -> list[str]:
    path = Path(topic_file_path)

    if not path.is_absolute():
        path = BACKEND_DIR / topic_file_path

    if not path.exists():
        raise FileNotFoundError(f"Topic file not found: {path}")

    topics = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            topic = line.strip()

            if topic and not topic.startswith("#"):
                topics.append(topic)

    return topics


def import_topics_from_file(
    topic_file_path: str,
    category: str = "general",
) -> dict[str, Any]:
    topics = read_topic_file(topic_file_path)

    results = []

    for topic in topics:
        result = import_topic_as_draft(topic, category)
        results.append(result)

    successful = [
        result for result in results
        if result.get("status") == "draft_created"
    ]

    failed = [
        result for result in results
        if result.get("status") != "draft_created"
    ]

    return {
        "status": "completed",
        "topic_file": topic_file_path,
        "category": category,
        "total_topics": len(topics),
        "successful_imports": len(successful),
        "failed_imports": len(failed),
        "results": results,
    }
