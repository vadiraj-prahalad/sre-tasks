from app.services.knowledge_repository import (
    add_knowledge_item,
    load_all_facts,
    update_answer,
    delete_knowledge_item,
    search_knowledge_items,
)

def list_knowledge():
    return load_all_facts()


def create_knowledge_item(item: dict) -> None:
    required_fields = [
        "canonical_question",
        "answer",
        "category",
        "canonical_key",
        "title",
        "domain",
    ]

    missing_fields = []

    for field in required_fields:
        if not item.get(field):
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    add_knowledge_item(item)


def update_knowledge_answer(
    canonical_key: str,
    answer: str,
) -> None:
    update_answer(canonical_key, answer)

def delete_knowledge(canonical_key: str) -> None:
    delete_knowledge_item(canonical_key)

def search_knowledge(search_text: str) -> list[dict]:
    return search_knowledge_items(search_text)
