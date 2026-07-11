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