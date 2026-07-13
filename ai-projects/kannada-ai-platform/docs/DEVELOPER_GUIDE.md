
# Entity Classification Development Guide

## Purpose

Entity classification converts trusted provider metadata into canonical
platform entity types.

Example:

Wikidata P31 Q5
    ↓
PERSON

## Classification Pipeline

1. Resolve the user query.
2. Collect provider evidence.
3. Fetch the exact Wikidata entity when a Q-ID is available.
4. Extract P31 instance-of IDs.
5. Preserve metadata through evidence normalization.
6. Enrich the immutable KnowledgeEntity.
7. Classify the entity using deterministic mappings.
8. Continue to editorial generation.

## Files

- app/services/internet_providers/wikidata_provider.py
- app/services/evidence_conflict_service.py
- app/services/entity_classification_service.py
- app/services/internet_knowledge_service.py
- app/db/tools/test_wikidata_claim_extraction.py
- app/db/tools/test_entity_classification.py
- app/db/tools/test_editorial_pipeline.py

## Adding a New Entity Type

Add a verified mapping to:

app/services/entity_classification_service.py

Example:

WIKIDATA_INSTANCE_OF_TYPE_MAP = {
    "Q5": "PERSON",
}

Requirements:

- verify the Wikidata item;
- add a focused test;
- confirm GENERAL fallback remains safe;
- run the editorial integration test;
- do not place platform mappings in provider code.

## Validation Commands

From backend:

python -m py_compile \
  app/services/entity_classification_service.py \
  app/services/internet_knowledge_service.py \
  app/db/tools/test_entity_classification.py \
  app/db/tools/test_editorial_pipeline.py

python -m app.db.tools.test_wikidata_claim_extraction

python -m app.db.tools.test_entity_classification

python -m app.db.tools.test_editorial_pipeline

python -m app.db.tools.test_entity_resolution

## Expected Behavior

Entity resolution alone:

Entity Type: GENERAL

Complete acquisition pipeline with Q5 evidence:

Entity Type: PERSON

This difference is intentional because classification occurs only after
trusted evidence becomes available.
