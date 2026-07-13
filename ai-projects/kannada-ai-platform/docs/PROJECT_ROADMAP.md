
# Phase 6 Progress — Entity Classification

## Phase 6.1 — Structured Type Metadata

Status: COMPLETE

Completed:

- Wikidata claims retrieval.
- P31 instance-of extraction.
- instance_of_ids metadata.
- evidence metadata propagation.
- focused extraction tests.
- live provider validation.

## Phase 6.2A — Deterministic Person Classification

Status: COMPLETE

Completed:

- dedicated classification service;
- Q5 to PERSON mapping;
- immutable KnowledgeEntity replacement;
- safe GENERAL fallback;
- preservation of existing non-GENERAL types;
- editorial pipeline integration;
- focused classification tests;
- end-to-end integration validation.

## Phase 6.2B — Classification Registry Expansion

Status: NEXT

Goal:

Support a small, verified Beta v1 taxonomy without redesigning the classifier.

Candidate types:

- PLACE
- ORGANIZATION
- TEMPLE
- FESTIVAL
- BOOK
- EVENT

Requirements:

- verify every Wikidata mapping;
- define precedence for multiple P31 values;
- retain GENERAL fallback;
- add unit and integration tests;
- avoid heuristic or LLM classification.

## Phase 6.3 — Type-Aware Editorial Behavior

Future:

- PERSON editorial template;
- PLACE editorial template;
- TEMPLE editorial template;
- BOOK editorial template;
- type-specific required fields;
- type-aware validation.

## Phase 7 Preparation

Typed KnowledgeEntity objects become the node foundation for the Knowledge Graph.
