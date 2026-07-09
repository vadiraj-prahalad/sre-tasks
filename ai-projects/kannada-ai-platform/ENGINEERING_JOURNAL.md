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