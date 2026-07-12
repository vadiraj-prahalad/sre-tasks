from app.services.entity_resolution_service import resolve_entity


def run() -> None:
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
        entity = resolve_entity(topic, category)

        entity_changed = (
            entity.resolved_topic != entity.original_query
        )

        print(f"Input          : {entity.original_query}")
        print(f"Normalized     : {entity.normalized_query}")
        print(f"Resolved       : {entity.resolved_topic}")
        print(f"Preferred Name : {entity.preferred_name}")
        print(f"Changed        : {entity_changed}")
        print(f"Entity Type    : {entity.entity_type}")
        print(f"Domain         : {entity.domain}")
        print(f"Confidence     : {entity.confidence}")
        print(f"Method         : {entity.resolution_method}")
        print("-" * 70)


if __name__ == "__main__":
    run()