# Kannada AI Platform Roadmap

## Vision
Build a trusted Kannada knowledge assistant that retrieves from curated and trustworthy sources, answers in Kannada, and shows source attribution.

## Current Architecture

React UI
→ FastAPI
→ Router
→ Curated Knowledge
→ RAG Service
→ Retriever Service
→ SQLite Documents/Chunks/Embeddings
→ Ollama LLM

## Completed

- FastAPI backend
- React frontend MVP
- SQLite knowledge store
- CRUD utilities
- Alias resolution
- RAG documents and chunks
- Embeddings with Ollama
- Semantic search
- Hybrid ranking
- Source attribution
- Answer strategy
- Knowledge manifest
- Multi-document ingestion
- Retriever service refactor

## Current Phase
Phase 4: Scalable Knowledge Acquisition

## Next Milestones

### Backend
- Improve retriever source selection
- Add document loader abstraction
- Add better chunking with overlap
- Add trust-level metadata
- Add source versioning
- Add Wikipedia/manual URL ingestion later

### Frontend
- Refactor into components
- Improve source display
- Add suggested questions
- Add categories
- Make mobile-first UI

### Production
- Dockerize backend/frontend
- Add deployment
- Add monitoring
- Add CI checks

## Release Target
Private beta before end of July with:
- React UI
- trusted sources
- semantic retrieval
- source-backed answers

## Current Phase

Phase 4.2
Knowledge Refresh Pipeline

Completed
----------
✓ Hybrid Retrieval
✓ Confidence Engine
✓ Developer Trace
✓ Alias Resolution
✓ Evaluation Framework

Next
-----
- Automatic Refresh Pipeline
- Incremental Embeddings
- Source Versioning

Current Phase

Phase 4.3

Editorial Knowledge Generation

Completed

✓ GPT-5.5 Editorial Engine
✓ AI Provider Layer
✓ Editorial Prompt v2
✓ Editorial Usage Logging
✓ Cost Tracking
✓ Human Editorial Workflow

Next

- 10 Topic Benchmark
- Category-specific Editorial Templates
- Bulk Import (500 Topics)
- Bulk Import (1000 Topics)
- Beta UI Polish
- Feedback Analytics

---

# Phase 4.3 Completed

## Trusted Editorial Knowledge Acquisition

### Completed

✓ Entity Resolution

✓ Canonical Alias Mapping

✓ Wikipedia Metadata

✓ Exact Wikidata Lookup

✓ Evidence Builder

✓ Evidence Quality Service

✓ Evidence Conflict Detection

✓ GPT-5.5 Editorial Generation

✓ Human Draft Queue

---

# Current Phase

## Phase 4.4 — Editorial Validation & Publishing

### Goals

- Editorial Review Workflow
- Approve / Reject Pipeline
- Publish to Knowledge Base
- Automatic Embedding Generation
- Knowledge Version History
- Incremental Refresh

## Phase 5 — Canonical Knowledge Model

Status

In Progress

Completed

✅ KnowledgeEntity model

✅ Entity Resolver returns KnowledgeEntity

Next

⬜ Canonical English title

⬜ Wikidata ID

⬜ Canonical Kannada title

⬜ Entity Type

⬜ Replace remaining string-based pipeline

Phase 5 ✅ COMPLETE

Canonical Knowledge Model

Next

Phase 6

Automatic Entity Classification

Goal

KnowledgeEntity should automatically infer

- PERSON
- PLACE
- EVENT
- BOOK
- FESTIVAL
- TEMPLE
- ORGANIZATION

without relying on manual categories.

Phase 6

✓ 6.1 Entity Classification

✓ 6.2 Editorial Quality Gate

⬜ 6.3 Editorial Policy Engine

⬜ 6.4 Citation-aware Articles

⬜ 6.5 Knowledge Graph