from app.services.entity_resolution_service import resolve_entity


def run():
    tests = [
        ("Basavanna", "religion"),
        ("Basaveshwara", "religion"),
        ("Basava", "religion"),
        ("Mysore Palace", "location"),
        ("Bangalore", "location"),
        ("Unknown Topic", "general"),
    ]

    print("=" * 70)
    print("Entity Resolution Test")
    print("=" * 70)

    for topic, category in tests:
        result = resolve_entity(topic, category)

        print(f"Input      : {topic}")
        print(f"Resolved   : {result['resolved']}")
        print(f"Changed    : {result['changed']}")
        print(f"Category   : {result['category']}")
        print("-" * 70)


if __name__ == "__main__":
    run()
