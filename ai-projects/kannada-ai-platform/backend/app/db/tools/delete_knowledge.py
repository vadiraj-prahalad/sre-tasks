from app.services.knowledge_admin_service import delete_knowledge


def main() -> None:
    canonical_key = "madhwacharya"

    delete_knowledge(canonical_key)

    print("Knowledge deleted successfully.")


if __name__ == "__main__":
    main()
