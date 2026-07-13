"""
Wikidata Claim Extraction Test
==============================

Purpose
-------
Validate conversion of Wikidata structured claims into normalized
entity IDs without making an internet request.

The Phase 6 entity-classification pipeline depends on reliable
extraction of P31 instance-of values.
"""

from app.services.internet_providers.wikidata_provider import (
    WikidataProvider,
)


def run() -> None:
    """
    Test valid, duplicate, missing, malformed, and invalid claims.
    """

    claims = {
        "P31": [
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "entity-type": "item",
                            "numeric-id": 5,
                            "id": "Q5",
                        },
                        "type": (
                            "wikibase-entityid"
                        ),
                    }
                }
            },
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "entity-type": "item",
                            "numeric-id": 5,
                            "id": "q5",
                        },
                        "type": (
                            "wikibase-entityid"
                        ),
                    }
                }
            },
            {
                "mainsnak": {
                    "snaktype": "novalue",
                }
            },
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "id": "P31",
                        }
                    }
                }
            },
            {
                "mainsnak": {
                    "datavalue": {
                        "value": {
                            "id": "invalid",
                        }
                    }
                }
            },
        ]
    }

    instance_of_ids = (
        WikidataProvider
        ._extract_entity_ids_from_claims(
            claims=claims,
            property_id="P31",
        )
    )

    assert instance_of_ids == [
        "Q5"
    ], (
        "Expected ['Q5'], received "
        f"{instance_of_ids}"
    )

    lowercase_property_ids = (
        WikidataProvider
        ._extract_entity_ids_from_claims(
            claims=claims,
            property_id="p31",
        )
    )

    assert lowercase_property_ids == [
        "Q5"
    ], (
        "Property IDs should be normalized "
        "to uppercase."
    )

    missing_property_ids = (
        WikidataProvider
        ._extract_entity_ids_from_claims(
            claims=claims,
            property_id="P279",
        )
    )

    assert missing_property_ids == [], (
        "Missing properties must return "
        "an empty list."
    )

    malformed_claims_result = (
        WikidataProvider
        ._extract_entity_ids_from_claims(
            claims={
                "P31": [
                    {},
                    {
                        "mainsnak": {},
                    },
                    {
                        "mainsnak": {
                            "datavalue": {
                                "value": (
                                    "invalid"
                                ),
                            }
                        }
                    },
                    "invalid claim",
                ]
            },
            property_id="P31",
        )
    )

    assert malformed_claims_result == [], (
        "Malformed claims must be ignored."
    )

    invalid_claim_collection = (
        WikidataProvider
        ._extract_entity_ids_from_claims(
            claims={
                "P31": "not-a-list",
            },
            property_id="P31",
        )
    )

    assert invalid_claim_collection == [], (
        "Non-list property values must "
        "return an empty list."
    )

    invalid_claims_object = (
        WikidataProvider
        ._extract_entity_ids_from_claims(
            claims=[],
            property_id="P31",
        )
    )

    assert invalid_claims_object == [], (
        "Non-dictionary claims input must "
        "return an empty list."
    )

    empty_property = (
        WikidataProvider
        ._extract_entity_ids_from_claims(
            claims=claims,
            property_id="",
        )
    )

    assert empty_property == [], (
        "Empty property IDs must return "
        "an empty list."
    )

    print("=" * 72)
    print(
        "Wikidata Claim Extraction Test"
    )
    print("=" * 72)
    print(
        f"Extracted P31 IDs: {instance_of_ids}"
    )
    print(
        "Duplicate handling       : PASS"
    )
    print(
        "Case normalization       : PASS"
    )
    print(
        "Missing property handling: PASS"
    )
    print(
        "Malformed claim handling : PASS"
    )
    print(
        "Invalid input handling   : PASS"
    )
    print("=" * 72)


if __name__ == "__main__":
    run()