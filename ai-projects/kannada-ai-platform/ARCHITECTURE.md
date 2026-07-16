# Kannada AI Platform Architecture

React UI

↓

FastAPI

↓

Router

↓

Alias Resolver

↓

Known Facts

↓

RAG Retriever

↓

SQLite

↓

Embeddings

↓

Answer Strategy

↓

Confidence Engine

↓

Developer Trace

↓

Frontend


## Architecture

The current MVP architecture is documented here:

- [Architecture v1](docs/architecture/architecture-v1.png)

The system follows a knowledge-first approach:

```text
User
 ↓
FastAPI
 ↓
Router
 ↓
Query Normalizer
 ↓
Knowledge Service
 ↓
Knowledge Repository
 ↓
Trusted Kannada JSON Data

Fallback:
Router
 ↓
Local LLM
 ↓
Ollama / Llama3

## Current Status

Version: Beta 0.4

Completed

✅ Knowledge Engine
✅ RAG
✅ Knowledge Packs
✅ Feedback System
✅ Draft Queue
✅ Domain Safety
✅ Related Topics

Next

- Conversation Memory
- Admin Dashboard
- Production Deployment
````

---

# Architecture Update — 2026-07-10 (Version Beta 0.5)

## Trusted Editorial Knowledge Acquisition Pipeline

The editorial pipeline evolved from a simple Wikipedia importer into a modular knowledge acquisition architecture.

```text
User Topic
      │
      ▼
Entity Resolver
      │
      ▼
Internet Knowledge Collection
      ├───────────────┬──────────────┐
      ▼               ▼              ▼
Kannada Wikipedia  English Wikipedia  Wikidata
      │               │               │
      └───────────────┴───────────────┘
                      │
                      ▼
          Evidence Quality Service
                      │
                      ▼
            Evidence Builder Service
                      │
                      ▼
         Evidence Conflict Detection
                      │
                      ▼
      Editorial Prompt Builder (GPT-5.5)
                      │
                      ▼
         Human Editorial Draft Queue
                      │
                      ▼
      Future Publishing Pipeline
```

## Overall Platform Architecture

```text
React UI
    │
FastAPI
    │
Router
    │
────────────────────────────────────────────
│ Runtime AI           Editorial AI        │
│                                          │
│  RAG                 Entity Resolution   │
│  Retriever           Evidence Builder    │
│  Ollama              Conflict Detection  │
│                      GPT-5.5 Editorial   │
────────────────────────────────────────────
            │
            ▼
SQLite Knowledge Base
            │
Embeddings
            │
Runtime Answers
```

## Python Execution Flow

```text
manage.py
      │
      ▼
import_topic_as_draft()
      │
resolve_entity()
      │
collect_topic_evidence()
      │
Wikipedia / Kannada Wikipedia / Wikidata
      │
successful_sources()
      │
select_clean_evidence()
      │
build_evidence()
      │
analyze_evidence_conflicts()
      │
generate_editorial_draft()
      │
save_draft_answer()
```

### Version

Current Version: **Beta 0.5**

---

# 2026-07-11 — Architecture Evolution

## Major Architectural Decision

The project officially begins transitioning from a **string-driven knowledge pipeline** to a **Canonical Knowledge Model**.

Old Flow

User Query
    ↓
Resolved Topic (string)
    ↓
Evidence Collection
    ↓
Editorial Prompt
    ↓
LLM

New Target Flow

User Query
    ↓
Entity Resolution
    ↓
KnowledgeEntity
    ↓
Evidence Collection
    ↓
Editorial AI
    ↓
Human Review
    ↓
Published Knowledge

KnowledgeEntity will become the single source of truth throughout the platform.

# 2026-07-12 — Canonical Knowledge Model Completed

## Objective

Replace loosely-coupled string-based topic handling with a canonical
KnowledgeEntity model shared across the editorial acquisition pipeline.

## Major Architecture Changes

User Query
    ↓
KnowledgeEntity
    ↓
Evidence Collection
    ↓
Evidence Validation
    ↓
Entity Enrichment
    ↓
Editorial Draft
    ↓
Human Review

## New Core Components

- app/models/knowledge_entity.py
- entity_resolution_service.py
- entity_enrichment_service.py

## Updated Components

- internet_knowledge_service.py
- evidence_conflict_service.py
- editorial pipeline integration

## Architectural Principles

• Identity exists independently of evidence.
• Evidence enriches identity.
• Editorial generation consumes canonical entities.
• Human review remains the publication gate.

Status:
Frozen for Beta v1.

# Phase 6.2 — Deterministic Editorial Quality Gate

The editorial pipeline now includes a deterministic validation layer between AI generation and human review.

Updated pipeline

Internet
    │
    ▼
Entity Resolution
    │
    ▼
Evidence Collection
    │
    ▼
Evidence Cleaning
    │
    ▼
Conflict Detection
    │
    ▼
Entity Enrichment
    │
    ▼
Entity Classification
    │
    ▼
Editorial Draft (LLM)
    │
    ▼
Editorial Validator
    │
    ▼
Draft Database
    │
    ▼
Admin Review Portal
    │
    ▼
Human Approval
    │
    ▼
Knowledge Base

The Editorial Validator performs deterministic checks before drafts enter the CMS workflow.

Validation includes:

- Required article sections
- Duplicate paragraph detection
- Placeholder detection
- English leakage detection
- Kannada content ratio validation
- Minimum article size

---

# 2026-07-15 — Retrieval Quality Foundation (Phase 6.2B)

## Objective

Strengthen retrieval quality before expanding additional platform intelligence.

Rather than immediately implementing more entity types or retrieval heuristics,
the project first establishes measurable retrieval quality, deterministic
ranking behaviour, and retrieval observability.

This milestone follows the engineering principle:

Measure first.
Optimize second.

---

## Updated Runtime Retrieval Flow

User Query
    ↓
Query Normalization
    ↓
Canonical Entity Resolution
    ↓
Hybrid Retriever Ranking V1
    │
    ├── Semantic Embedding Similarity
    │
    ├── Content Keyword Overlap
    │
    ├── Title Keyword Overlap
    │
    └── Score Bounding (≤ 1.0)
    ↓
Top Ranked Knowledge Chunks
    ↓
RAG Context Builder
    ↓
Local LLM (Ollama)
    ↓
Grounded Kannada Answer

---

## Hybrid Retriever Ranking V1

Current ranking combines three deterministic signals.

Final Score

Semantic Similarity
        +
Content Overlap Bonus
        +
Title Overlap Bonus

Final score is bounded to 1.0.

Generic Kannada question words are intentionally excluded from lexical scoring.

Ignored examples:

- ಯಾರು
- ಏನು
- ಬಗ್ಗೆ
- ಹೇಳಿ
- ಎಂದರೇನು

This prevents question structure from influencing retrieval ranking.

---

## Retrieval Evaluation Architecture

Retrieval quality is now measured independently of answer generation.

Evaluation metrics include:

- Hit@1
- Hit@3
- Mean Reciprocal Rank (MRR)
- Retrieval latency
- Semantic score
- Content bonus
- Title bonus

This allows retrieval regressions to be detected before they affect runtime answers.

---

## Retrieval Observability

Developer Trace now exposes retrieval internals.

For every retrieved document the platform records:

- semantic similarity
- content overlap bonus
- title overlap bonus
- raw retrieval score
- bounded score
- source collection
- document provenance

This enables deterministic debugging of retrieval behaviour.

---

## Canonical Entity Alias Layer

Canonical aliases remain outside the retriever.

User Query
    ↓
Entity Resolution
    ↓
Canonical Identity
    ↓
Retriever

Recently expanded coverage includes canonical aliases for:

- Dr Rajkumar
- Kannada spellings
- honorific forms
- popular titles
- English variants

The retriever operates only on canonical queries.

---

## Responsibility Boundaries

### Deterministic Python

Responsible for:

- query normalization
- canonical entity resolution
- retrieval ranking
- evidence collection
- evidence normalization
- provenance tracking
- evaluation
- confidence calculation

### Local Runtime LLM

Responsible for:

- grounded Kannada generation
- summarization
- natural language synthesis

The runtime LLM does not perform retrieval ranking or canonical entity resolution.

---

## Current Retrieval Baseline

Measured baseline:

Hit@1

90%

Hit@3

90%

End-to-end RAG evaluation

10 / 10 Passed

The remaining retrieval failure is intentionally preserved as a measurable baseline
rather than hidden through additional retrieval heuristics.

---

## Architectural Decision

Retrieval quality now becomes a prerequisite for future platform capabilities.

Future work will improve retrieval only after measurable evidence demonstrates
a genuine limitation.

This prevents premature optimization and preserves deterministic system behaviour.

Status:

Phase 6.2B complete.

Next:

Phase 6.2C — Classification Registry Expansion