from app.services.knowledge_admin_service import list_knowledge


def main() -> None:
    facts = list_knowledge()

    if not facts:
        print("No knowledge items found.")
        return

    print("\nKannada Knowledge Items\n")
    print("-" * 80)

    for index, (question, answer) in enumerate(facts.items(), start=1):
        print(f"ID: {index}")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("-" * 80)


if __name__ == "__main__":
    main()
