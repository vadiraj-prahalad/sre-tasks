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
