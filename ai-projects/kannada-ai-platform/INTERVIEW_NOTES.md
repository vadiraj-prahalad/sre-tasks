# Interview Notes

## Implemented

Hybrid Retrieval

Confidence Engine

Developer Trace

Curated Knowledge

Alias Resolution

Answer Evaluation

## Design Patterns

Repository

Service Layer

Router Pattern

Strategy Pattern

## Interview Topics

What is RAG?

How are embeddings used?

How does semantic search work?

How do you evaluate AI quality?

Why confidence scoring?

## Editorial Architecture

Implemented

- AI Provider Pattern
- GPT-5.5 Editorial Pipeline
- Editorial Prompt Engineering
- Cost Monitoring
- Provider Abstraction

Design Patterns

- Strategy Pattern
- Provider Pattern
- Service Layer
- Dependency Inversion

Interview Questions

Why separate content generation from inference?

How would you replace GPT with Gemini?

Why use abstraction?

How do you measure AI cost?

How do you improve AI answer quality?

---

# Editorial Knowledge Acquisition

## New Components

- Entity Resolution
- Evidence Builder
- Evidence Quality Service
- Evidence Conflict Detection
- Exact Wikidata Lookup

## Design Patterns

- Pipeline Pattern
- Provider Pattern
- Strategy Pattern
- Single Responsibility Principle

## Common Interview Questions

### Why Entity Resolution?

Normalizes user input into a canonical entity before retrieval.

### Why Exact Wikidata Lookup?

Text search may return unrelated entities.
Wikipedia provides the correct Wikidata Q-ID.

### Why Evidence Builder?

Every provider returns different fields.
Evidence Builder converts them into one common schema.

### Why Conflict Detection?

Different trusted sources may disagree.
The AI should avoid presenting uncertain facts as absolute truth.

### Why Metadata?

Metadata enables richer validation and future features like images, coordinates and infoboxes.

## 2026-07-11

Question

Why introduce a KnowledgeEntity model?

Answer

Knowledge systems should pass semantic objects rather than raw strings.
A KnowledgeEntity encapsulates identity, aliases, canonical names, entity type, confidence and metadata, allowing every downstream component to consume consistent information.

Design Pattern

Rich Domain Model

Benefits

- Less duplication
- Better maintainability
- Easier testing
- Future extensibility

## Interview Topic

Why create a domain model instead of passing dictionaries?

Answer

A domain model centralizes business meaning.

Instead of passing loosely-defined dictionaries or strings across
multiple services, every component consumes the same strongly-defined
object.

Advantages

• Better maintainability
• Easier testing
• Easier extension
• Reduced coupling
• Better readability