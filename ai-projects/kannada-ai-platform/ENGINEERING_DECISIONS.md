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