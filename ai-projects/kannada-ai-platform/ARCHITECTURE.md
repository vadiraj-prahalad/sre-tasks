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