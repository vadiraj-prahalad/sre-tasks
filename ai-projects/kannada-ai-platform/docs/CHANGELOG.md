# Changelog

## 2026-07-07

### Added

- Feedback API
- Feedback Dashboard
- Domain Classifier
- Religion Knowledge Pack
- Safety Guardrails
- Related Topics
- Developer Mode
- Confidence Improvements

### Improved

- Trust UI
- Sources
- Related Topics placement
- Roman aliases

### Fixed

- Madhwacharya normalization
- Kuvempu evaluation
- Alias routing

## 2026-07-13

### Added

- Wikidata structured claim retrieval.
- P31 instance-of ID extraction.
- Entity classification service.
- Deterministic Q5 to PERSON mapping.
- Focused Wikidata claim extraction test.
- Focused entity classification test.

### Changed

- Exact Wikidata lookup now retrieves claims.
- Evidence metadata now preserves instance_of_ids.
- Editorial acquisition pipeline now classifies enriched entities.
- Editorial integration output now exposes typed entities.

### Validated

- Wikidata P31 extraction with mocked data.
- Live Wikidata API response for Kempe Gowda I.
- Immutable KnowledgeEntity replacement.
- GENERAL fallback for unknown and malformed metadata.
- Existing entity resolution behavior.
- End-to-end editorial pipeline classification.

### Current Result

Kempe Gowda I:
- Wikidata ID: Q6387049
- P31: Q5
- Entity Type: PERSON
