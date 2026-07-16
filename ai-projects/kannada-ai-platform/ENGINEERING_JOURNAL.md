# Engineering Journal

---

# Day 1 — Knowledge Platform Foundation

## Goal

Improve the Kannada AI Platform from a simple chatbot into a trustworthy knowledge platform.

## Completed

- Improved RAG pipeline
- Hybrid Retriever
- Alias Resolution
- Confidence Engine
- Developer Trace
- Knowledge Evaluation Pipeline
- Curated Knowledge Routing
- Source Attribution

## Major Learnings

- Retrieval is more important than prompting.
- Confidence scoring increases user trust.
- Developer Trace makes debugging much easier.
- Evaluation scripts prevent regressions.

## Challenges

- Alias matching inconsistencies
- Knowledge selection
- Answer quality tuning
- Retrieval ranking

## Next Goal

Scalable Knowledge Acquisition

## Interview Questions

- Explain RAG.
- Explain Hybrid Retrieval.
- Why Confidence Score?
- Why Trace Mode?
- Why Curated Knowledge?

---

# Day 2 — Editorial AI Pipeline

## Goal

Improve Kannada knowledge quality for Beta release.

## Completed

- GPT-5.5 Editorial Integration
- AI Provider Layer
- Editorial Prompt Builder
- Usage Logging
- Cost Tracking
- Prompt Guardrails
- Provider Switching

## Major Learnings

- Runtime LLM and Editorial LLM should be different.
- GPT-5.5 produces significantly better Kannada than local Llama.
- Provider abstraction enables future AI providers.
- Prompt engineering affects article quality more than expected.

## Challenges

- Empty responses due to reasoning tokens.
- Mixed-language output.
- Prompt refinement.
- Editorial prioritization.

## Next Goal

Benchmark 10 representative topics.

Generate first 500 high-quality draft articles.

## Interview Topics

Why separate runtime AI and editorial AI?

Explain Provider Pattern.

Why prompt engineering matters.

Why not generate knowledge at runtime?

How do you control AI costs?

---

# Day 3 — Trusted Editorial Knowledge Acquisition

## Goal

Transform the editorial importer into a reliable, modular knowledge acquisition pipeline.

## Completed

- Entity Resolution Service
- Canonical alias mapping
- Wikipedia metadata extraction
- Exact Wikidata lookup using Wikipedia Q-ID
- Evidence Builder
- Evidence Quality Service
- Evidence Conflict Detection
- Editorial warnings
- Modular editorial architecture

## Major Learnings

- Exact identifiers are more reliable than text search.
- Metadata is valuable beyond summaries.
- Editorial AI should receive validated evidence.
- Evidence validation improves trustworthiness.

## Challenges

- Wikidata fuzzy search selected incorrect entities.
- Conflicting years between providers.
- Kannada Wikipedia coverage was inconsistent.
- Evidence normalization across providers.

## Next Goal

Phase 4.4 — Editorial Validation & Publishing

## Interview Questions

- Why use canonical entity resolution?
- Why separate evidence collection from prompting?
- Why detect evidence conflicts?
- Why prefer exact Wikidata lookup?
- Why normalize provider output?

# Engineering Journal

## 2026-07-11

Today's work focused less on features and more on long-term architecture.

Major accomplishments:

- Editorial language quality improved.
- Publication-quality style guide expanded.
- Editorial checklist introduced.
- KnowledgeEntity model introduced.
- Entity Resolution migrated to KnowledgeEntity.

Most important lesson:

Prompt engineering alone cannot solve language quality.
A better knowledge model produces better prompts automatically.

# Day Summary

Completed Canonical Knowledge Model.

Major achievements

✓ Introduced immutable KnowledgeEntity
✓ Added entity enrichment
✓ Refactored editorial acquisition
✓ Added integration testing
✓ Removed false-positive year conflicts
✓ Fixed pipeline metadata propagation

Key lesson

Architecture should model the domain, not merely move strings between services.

Next milestone

Automatic Entity Type & Domain Inference.

# 2026-07-14

Objective

Introduce a deterministic editorial quality gate.

Completed

✓ Editorial validator service

✓ Pipeline integration

✓ Draft validation metadata

✓ Admin validation panel

✓ Validation projection

✓ Regression tests

Issue encountered

Kannada ratio exceeded 1.0.

Root cause

Kannada characters were counted differently from alphabetic characters.

Resolution

Calculate

Kannada alphabetic letters
---------------------------
Total alphabetic letters

Result

Ratio now always remains between 0 and 1.

Outcome

Editorial drafts now undergo deterministic validation before reaching reviewers.

# 2026-07-15

## Objective

Improve retrieval quality without introducing unnecessary complexity.

## Completed

✓ Hybrid Retriever Ranking V1 stabilized

✓ Retrieval Baseline Evaluator

✓ Provenance-aware retrieval diagnostics

✓ Canonical Rajkumar aliases

✓ Retrieval observability

## Major Investigation

The Kuvempu ranking regression initially appeared to be an embedding problem.

Investigation confirmed:

- document existed;
- chunk existed;
- embedding existed;
- indexing was correct.

Root cause:

Ranking behaviour.

The retriever was rewarding generic Kannada question words rather than meaningful entity overlap.

Generic lexical terms were removed from scoring.

Hybrid ranking now combines:

- semantic similarity;
- content overlap;
- title overlap.

## Major Lesson

Measure retrieval before optimizing it.

Architecture improvements should be driven by measurable evidence rather than intuition.

## Outcome

Retrieval became easier to debug while preserving deterministic behaviour.

End-to-end RAG evaluation remained fully successful.

## Next Milestone

Entity-aware retrieval using canonical entities.