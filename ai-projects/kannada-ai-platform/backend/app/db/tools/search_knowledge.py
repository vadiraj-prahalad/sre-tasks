import sys

from app.services.knowledge_admin_service import search_knowledge


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.db.tools.search_knowledge <search_text>")
        return

    search_text = sys.argv[1]
    results = search_knowledge(search_text)

    if not results:
        print("No matching knowledge found.")
        return

    print("\nSearch Results\n")
    print("-" * 80)

    for item in results:
        print(f"Key: {item['canonical_key']}")
        print(f"Title: {item['title']}")
        print(f"Question: {item['canonical_question']}")
        print(f"Domain: {item['domain']}")
        print(f"Subdomain: {item['subdomain']}")
        print(f"Answer: {item['answer']}")
        print("-" * 80)


if __name__ == "__main__":
    main()
