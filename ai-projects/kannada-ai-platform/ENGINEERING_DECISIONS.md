# Engineering Decisions - Kannada AI Platform

## Purpose

This document explains why each script/service exists, what problem it solved, and how the architecture evolved.

---

## manage.py

### Problem
The project had many operational commands:

- ingest sources
- generate embeddings
- list documents
- evaluate RAG

Remembering long module commands was becoming difficult.

### Decision
Created `backend/manage.py` as a single command runner.

### Benefit
Simplifies operations:

```bash
python manage.py list
python manage.py sync
python manage.py evaluate

- 2026-07-06: The original v0.1 static JSON architecture evolved into a layered trusted-knowledge + RAG + Ollama fallback architecture with SQLite-backed knowledge stores, embeddings, confidence scoring, developer trace, and PWA frontend.

---

## Decision: Separate Editorial AI from Runtime AI

### Date

2026-07-09

### Problem

Local Llama generated inconsistent Kannada while importing trusted knowledge.

Examples included:

- Literal translations
- Broken Kannada words
- Mixed-language output

### Alternatives Considered

- Improve Ollama prompts
- Continue manual editing
- Use GPT-5 mini
- Use GPT-5.5

### Decision

Use GPT-5.5 only during editorial knowledge generation.

Continue serving approved knowledge using local Llama.

### Benefits

- Excellent Kannada quality
- Low operational cost
- Offline runtime
- Provider-independent architecture

### Future

Gemini and Claude can later plug into the same provider interface without changing business logic.

---

# Decision: Separate Evidence Collection from Editorial Generation

## Date

2026-07-10

## Problem

Initially the editorial pipeline directly consumed raw provider responses.

This tightly coupled:

- Internet providers
- Evidence filtering
- Editorial prompting

Adding new providers or validating evidence would require modifying multiple services.

## Decision

Split the pipeline into independent stages.

Internet Providers
↓

Evidence Quality

↓

Evidence Builder

↓

Conflict Detection

↓

Editorial Prompt

↓

GPT-5.5

↓

Draft Queue

## Benefits

- Easier to extend
- Better testing
- Cleaner architecture
- Easier debugging
- Supports future providers

## Future

This architecture allows adding Britannica, government datasets or Kannada encyclopedias without changing the editorial workflow.

## Interview Explanation

This follows the Single Responsibility Principle.

Each service performs one job:

- Providers fetch.
- Quality filters.
- Builder normalizes.
- Conflict detector validates.
- Editorial AI writes.

# Decision — Canonical Knowledge Model

Date:
2026-07-11

Decision:

The system will migrate from passing primitive strings between services to passing a KnowledgeEntity object.

Reason:

- Reduces duplicated logic.
- Centralizes canonical identity.
- Simplifies prompt generation.
- Improves retrieval.
- Simplifies future multilingual support.
- Better scalability.

Status:
Approved

# Decision 012 — Introduce KnowledgeEntity

## Problem

The acquisition pipeline passed raw strings between services.

This caused duplicated parsing, inconsistent metadata, and tightly
coupled downstream components.

## Decision

Introduce an immutable KnowledgeEntity model.

The object becomes the canonical representation of every topic.

## Consequences

Benefits

- One source of truth
- Easier testing
- Future knowledge graph support
- Cleaner prompt generation
- Better retrieval

Tradeoffs

- Slightly larger model
- Requires enrichment stage

Decision Status

Accepted
Frozen

## Decision 024

Title

Deterministic validation before human review

Problem

LLMs occasionally generate structurally invalid encyclopedia articles.

Decision

Introduce a deterministic validation layer before draft storage.

Validator responsibilities

- Structure validation
- Kannada language ratio
- Duplicate detection
- Placeholder detection
- English leakage

Reason

Editorial quality should never depend solely on the LLM.

Status

Accepted

# Decision 014 — Measure Retrieval Before Optimizing

## Date

2026-07-15

## Problem

Retrieval improvements were being implemented without objective measurements.

This risked introducing additional heuristics without understanding the actual failure modes.

## Decision

Introduce a dedicated Retrieval Baseline Evaluator before further retriever enhancements.

The evaluator measures:

- Hit@1
- Hit@3
- Mean Reciprocal Rank
- Retrieval latency
- Semantic similarity
- Content overlap bonus
- Title overlap bonus

## Benefits

- Objective regression detection
- Repeatable benchmarking
- Data-driven optimization
- Safer architectural evolution

## Consequences

Future retrieval work must be justified by measured evidence rather than assumptions.

Status:

Accepted

---

# Decision 015 — Retrieval Observability

## Problem

Retrieval failures could not be explained from runtime output.

## Decision

Expose deterministic retrieval signals through Developer Trace.

Recorded signals include:

- semantic similarity
- content overlap
- title overlap
- bounded score
- document source
- document provenance

## Benefits

- Easier debugging
- Explainable retrieval
- Better production diagnostics
- Faster regression analysis

Status:

Accepted

---

# Decision 016 — Canonical Entity Resolution Before Retrieval

## Problem

Multiple spellings of the same entity produced inconsistent retrieval behaviour.

## Decision

Resolve canonical identity before retrieval.

Retrievers should operate on canonical entities instead of raw user text.

## Benefits

- Lower retriever complexity
- Better multilingual support
- Stable retrieval behaviour
- Cleaner architecture

Status:

Accepted