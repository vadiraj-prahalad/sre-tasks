
# 2026-07-13 — Structured Entity Classification

## Objective

Extend the Canonical Knowledge Model with deterministic entity classification
based on trusted Wikidata ontology metadata.

## Runtime Flow

User Query
    ↓
Entity Resolution
    ↓
KnowledgeEntity
    ↓
Evidence Collection
    ↓
Evidence Normalization
    ↓
Conflict Analysis
    ↓
Entity Enrichment
    ↓
Entity Classification
    ↓
Typed KnowledgeEntity
    ↓
Editorial Draft
    ↓
Human Review

## Wikidata Classification Flow

Wikipedia wikibase_item
    ↓
Exact Wikidata Lookup
    ↓
Wikidata Claims
    ↓
P31 — instance of
    ↓
instance_of_ids
    ↓
Entity Classification Service
    ↓
Platform Entity Type

Current verified mapping:

Q5 — human
    ↓
PERSON

## Architectural Boundaries

### Wikidata Provider

Responsible for:

- retrieving exact Wikidata entities;
- fetching claims;
- extracting normalized P31 entity IDs;
- returning provider metadata.

The provider must not assign platform-specific entity types.

### Evidence Pipeline

Responsible for:

- preserving structured metadata;
- removing noisy provider fields;
- detecting conflicting entity IDs;
- passing classification evidence safely downstream.

### Entity Classification Service

Responsible for:

- interpreting normalized instance-of IDs;
- mapping trusted ontology IDs to platform entity types;
- returning a new immutable KnowledgeEntity;
- preserving existing non-GENERAL classifications;
- falling back safely to GENERAL.

## Current Classification

Kempe Gowda I
    ↓
Wikidata Q6387049
    ↓
P31 = Q5
    ↓
PERSON

## Design Principles

- Structured metadata before heuristic inference.
- Deterministic rules before LLM classification.
- Providers retrieve facts; services interpret business meaning.
- Unknown types fall back to GENERAL.
- Classification must not mutate the original KnowledgeEntity.
- Canonical Knowledge Model remains frozen.

Status:

Phase 6.1 complete.
Phase 6.2A complete.
