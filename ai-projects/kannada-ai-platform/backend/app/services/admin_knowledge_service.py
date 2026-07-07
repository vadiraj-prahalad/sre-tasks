import json
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parents[2]
ADMIN_ARTICLES_PATH = BACKEND_DIR / "knowledge" / "raw" / "admin_articles.json"


def ensure_admin_articles_file() -> None:
    ADMIN_ARTICLES_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not ADMIN_ARTICLES_PATH.exists():
        ADMIN_ARTICLES_PATH.write_text("[]", encoding="utf-8")


def load_admin_articles() -> list[dict[str, Any]]:
    ensure_admin_articles_file()

    with ADMIN_ARTICLES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_admin_articles(articles: list[dict[str, Any]]) -> None:
    ensure_admin_articles_file()

    with ADMIN_ARTICLES_PATH.open("w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=2)


def list_admin_articles() -> list[dict[str, Any]]:
    return load_admin_articles()


def add_admin_article(
    question: str,
    answer: str,
    category: str,
    source: str = "admin_cms",
    language: str = "kn",
) -> dict[str, Any]:
    articles = load_admin_articles()

    new_article = {
        "question": question.strip(),
        "answer": answer.strip(),
        "category": category.strip(),
        "source": source,
        "language": language,
    }

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
