import json
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
ADMIN_ARTICLES_PATH = BACKEND_DIR / "knowledge" / "raw" / "admin_articles.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_admin_articles_file() -> None:
    ADMIN_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not ADMIN_ARTICLES_PATH.exists():
        ADMIN_ARTICLES_PATH.write_text("[]", encoding="utf-8")


def normalize_article(article: dict[str, Any]) -> dict[str, Any]:
    timestamp = article.get("created_at") or now_iso()

    return {
        "id": article.get("id") or str(uuid.uuid4()),
        "question": article.get("question", "").strip(),
        "answer": article.get("answer", "").strip(),
        "aliases": article.get("aliases", []),
        "category": article.get("category", "general").strip(),
        "subcategory": article.get("subcategory", ""),
        "related_topics": article.get("related_topics", []),
        "difficulty": article.get("difficulty", "basic"),
        "status": article.get("status", "published"),
        "source": article.get("source", "admin_cms"),
        "source_urls": article.get("source_urls", []),
        "language": article.get("language", "kn"),
        "reviewed_by": article.get("reviewed_by", "admin"),
        "reviewed_at": article.get("reviewed_at") or timestamp,
        "version": article.get("version", 1),
        "created_at": timestamp,
        "updated_at": article.get("updated_at") or timestamp,
    }


def load_admin_articles() -> list[dict[str, Any]]:
    ensure_admin_articles_file()

    with ADMIN_ARTICLES_PATH.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    normalized_articles = [normalize_article(article) for article in articles]

    if normalized_articles != articles:
        save_admin_articles(normalized_articles)

    return normalized_articles


def save_admin_articles(articles: list[dict[str, Any]]) -> None:
    ensure_admin_articles_file()

    with ADMIN_ARTICLES_PATH.open("w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=2)


def list_admin_articles() -> list[dict[str, Any]]:
    return load_admin_articles()


def get_admin_dashboard() -> dict[str, Any]:
    articles = load_admin_articles()
    categories = Counter(article.get("category", "general") for article in articles)
    statuses = Counter(article.get("status", "published") for article in articles)

    return {
        "total_articles": len(articles),
        "categories": dict(categories),
        "statuses": dict(statuses),
        "recent_articles": list(reversed(articles[-10:])),
    }


def add_admin_article(
    question: str,
    answer: str,
    category: str,
    source: str = "admin_cms",
    language: str = "kn",
    aliases: list[str] | None = None,
    related_topics: list[str] | None = None,
    source_urls: list[str] | None = None,
    subcategory: str = "",
    difficulty: str = "basic",
    status: str = "published",
    reviewed_by: str = "admin",
) -> dict[str, Any]:
    articles = load_admin_articles()
    timestamp = now_iso()

    new_article = normalize_article(
        {
            "id": str(uuid.uuid4()),
            "question": question,
            "answer": answer,
            "aliases": aliases or [],
            "category": category,
            "subcategory": subcategory,
            "related_topics": related_topics or [],
            "difficulty": difficulty,
            "status": status,
            "source": source,
            "source_urls": source_urls or [],
            "language": language,
            "reviewed_by": reviewed_by,
            "reviewed_at": timestamp,
            "version": 1,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
    )

    articles.append(new_article)
    save_admin_articles(articles)

    return {
        "status": "created",
        "article": new_article,
        "total_articles": len(articles),
    }


def delete_admin_article(index: int) -> dict[str, Any]:
    articles = load_admin_articles()

    if index < 0 or index >= len(articles):
        return {
            "status": "not_found",
            "index": index,
        }

    removed_article = articles.pop(index)
    save_admin_articles(articles)

    return {
        "status": "deleted",
        "index": index,
        "article": removed_article,
        "total_articles": len(articles),
    }

def delete_admin_article_by_id(article_id: str) -> dict[str, Any]:
    articles = load_admin_articles()

    for index, article in enumerate(articles):
        if article.get("id") == article_id:
            removed_article = articles.pop(index)
            save_admin_articles(articles)

            return {
                "status": "deleted",
                "article_id": article_id,
                "article": removed_article,
                "total_articles": len(articles),
            }

    return {
        "status": "not_found",
        "article_id": article_id,
    }