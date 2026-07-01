from app.services.knowledge_repository import add_knowledge_item, load_all_facts


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
