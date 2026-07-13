
# Decision 013 — Use Wikidata P31 for Entity Classification

## Problem

The platform could resolve canonical identity but all entities remained GENERAL.

Description keywords and LLM-based classification were considered unreliable,
language-dependent, and difficult to audit.

## Decision

Use structured Wikidata P31 instance-of claims as the primary classification
signal.

Example:

Q6387049
    P31
     ↓
Q5
     ↓
PERSON

## Alternatives Considered

### Description Keyword Matching

Rejected because:

- wording varies across languages;
- descriptions are incomplete;
- keyword collisions create false classifications;
- rules become difficult to maintain.

### LLM Classification

Rejected as the primary method because:

- output is non-deterministic;
- difficult to audit;
- costs and latency increase;
- hallucination risk conflicts with trust-first architecture.

### Classification Inside Wikidata Provider

Rejected because:

- provider code should retrieve and normalize external facts;
- platform taxonomy is business logic;
- provider reuse would be reduced;
- testing would require unnecessary HTTP mocking.

## Consequences

Benefits:

- deterministic;
- explainable;
- auditable;
- provider-independent business logic;
- safe GENERAL fallback;
- extensible mapping registry.

Tradeoffs:

- mapping registry requires maintenance;
- Wikidata ontology can contain broad or multiple P31 values;
- subclass reasoning is not yet implemented.

## Status

Accepted.

Phase 6.2A currently supports:

Q5 → PERSON
