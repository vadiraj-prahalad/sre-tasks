
# 2026-07-13 — Entity Classification Foundation

## What Was Built

- Retrieved Wikidata claims during exact entity lookup.
- Extracted P31 instance-of IDs.
- Preserved structured classification metadata through evidence cleaning.
- Added a dedicated entity classification service.
- Added deterministic Q5 to PERSON classification.
- Integrated typed entities into the editorial acquisition pipeline.
- Added focused and integration tests.
- Validated the real Wikidata response for Kempe Gowda I.

## Problem Solved

The platform knew canonical entity identity but could not determine what kind of
entity it represented.

Before:

Kempe Gowda I
Wikidata ID: Q6387049
Entity Type: GENERAL

After:

Kempe Gowda I
Wikidata ID: Q6387049
P31: Q5
Entity Type: PERSON

## Why It Matters

Typed entities enable:

- entity-specific editorial templates;
- type-aware validation;
- typed search;
- knowledge graph nodes;
- recommendations;
- structured metadata;
- analytics by entity type.

## Key Architectural Lesson

External providers should return normalized facts.

Business services should interpret those facts.

The Wikidata provider returns Q5.
The classification service decides that Q5 means PERSON.

## Tests Completed

- claim extraction;
- duplicate handling;
- malformed metadata handling;
- unknown type fallback;
- immutable replacement;
- existing type preservation;
- editorial integration;
- entity resolution regression;
- live Wikidata verification.

## Commits

8dc8d79 — Expose Wikidata instance-of metadata

68eb8b6 — Add deterministic person entity classification

## Next Milestone

Expand the classification registry using verified mappings for a small
Beta v1 taxonomy.

Candidate types:

- PLACE
- ORGANIZATION
- TEMPLE
- FESTIVAL
- BOOK
- EVENT

Do not add mappings until each Wikidata ID and expected behavior are verified.
