# Changelog

## 2026-07-08

### Added

- Confidence Engine
- Developer Trace
- Alias Resolution
- Curated Knowledge Routing
- Answer Quality Service
- Knowledge Evaluation

### Improved

- RAG Retrieval
- Answer Strategy
- Query Normalization

### Fixed

- Incorrect routing
- Multiple retrieval issues
- Answer consistency

## 2026-07-09

### Added

- GPT-5.5 Editorial Provider
- AI Provider Abstraction Layer
- Editorial Prompt Builder v2
- Editorial Cost Tracking
- Editorial Usage Logging

### Improved

- Kannada article quality
- Editorial consistency
- Category-aware prompting
- Prompt engineering

### Fixed

- Empty editorial responses
- GPT reasoning token issue
- Mixed-script response handling
- Editorial fallback logic

## 2026-07-10

### Added

- Entity Resolution Service
- Entity Alias JSON
- Evidence Builder Service
- Evidence Quality Service
- Evidence Conflict Detection Service
- Exact Wikidata lookup using Wikipedia Q-ID
- Wikipedia metadata support
- Editorial evidence warnings
- Canonical entity normalization

### Improved

- Editorial prompt quality
- Multi-provider evidence collection
- Wikipedia + Wikidata integration
- Source selection accuracy
- Draft article consistency
- Human review information

### Fixed

- Incorrect Wikidata entity matching
- Duplicate alias handling
- Wrong entity selected from fuzzy search
- Missing metadata support
- Editorial year conflicts
- Provider normalization


## 2026-07-11

### Added

- Introduced KnowledgeEntity domain model.
- Entity Resolver now returns KnowledgeEntity instead of dictionary.
- Added Editorial Evaluation Checklist.
- Expanded Kannada Language Rules.
- Expanded Kannada Editorial Style Examples.

### Improved

- Editorial prompt quality.
- Natural Kannada generation.
- Publication-quality editorial guidance.
- Human review workflow.

### Architecture

- Began migration towards Canonical Knowledge Model.

## 2026-07-12

### Added

- KnowledgeEntity domain model
- Entity enrichment service
- Editorial integration test

### Changed

- Editorial acquisition pipeline now operates on canonical entities.
- Evidence conflict detection simplified.
- Metadata propagation improved.

### Fixed

- Integration metadata loss
- False-positive year conflicts
- Entity propagation bug