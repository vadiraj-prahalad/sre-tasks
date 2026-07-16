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

## Editorial AI

The platform now separates knowledge creation from runtime inference.

```
Internet Sources
      │
      ▼
GPT-5.5 Editorial AI
      │
Human Review
      │
SQLite Knowledge Base
      │
Embeddings
      │
Runtime Llama
      │
Users
```

This architecture enables:

- High-quality Kannada
- Low inference cost
- Offline runtime
- Provider independence
````

## Recent Progress (2026-07-11)

The platform has entered the Canonical Knowledge Model phase.

Recent improvements include:

- KnowledgeEntity domain model
- Improved editorial prompting
- Publication-quality Kannada rules
- Editorial review checklist
- Better textbook-style Kannada generation

Current focus is improving the semantic quality of the knowledge pipeline before scaling to 1,000+ curated Kannada topics.

## Recent Progress (2026-07-15)

The platform completed its Retrieval Quality Foundation milestone.

Major improvements include:

- Hybrid Retriever Ranking V1
- Retrieval Baseline Evaluator
- Provenance-aware Developer Trace
- Canonical entity alias expansion
- Retrieval observability

The current retrieval pipeline combines:

- semantic similarity
- content overlap
- title overlap

while preserving deterministic behaviour and explainable ranking.

The next milestone introduces entity-aware retrieval using the existing canonical entity model without increasing architectural complexity.