ARCHITECTURE_CURRENT.md = current working system
ENGINEERING_DECISIONS.md = why we made major decisions
ArchitectureDiagram30June2026.jpeg = historical v0.1 visual
# Kannada AI Platform Architecture

Last Updated: 2026-07-07

## Current Features

### Backend
- FastAPI
- SQLite Knowledge Base
- RAG Retrieval
- Alias Resolver
- Query Normalizer
- Related Topics
- Confidence Engine
- Feedback API
- Feedback Dashboard CLI
- Draft Knowledge Queue
- Draft Approval
- Domain Classifier
- Sensitive Domain Safety Guardrail

### Knowledge Packs
- Literature
- Grammar
- Language
- Religion
- Culture

### Frontend
- React
- Trust Indicator
- Source Chips
- Related Topics
- Feedback Buttons
- Developer Mode
- Developer Trace

## Current Flow

User
    ↓
API
    ↓
Domain Classifier
    ↓
Query Normalizer
    ↓
Known Answer
    ↓
Alias Resolver
    ↓
RAG
    ↓
Safety Check
    ↓
LLM (General Only)
    ↓
Draft Queue (if needed)
    ↓
Response
