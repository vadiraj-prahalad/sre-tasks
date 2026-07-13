
## Current Architecture Milestone

The platform now supports deterministic entity classification using trusted
Wikidata ontology metadata.

Example:

Kempe Gowda I
    ↓
Wikidata Q6387049
    ↓
P31 = Q5
    ↓
PERSON

Current supported platform entity types:

- GENERAL
- PERSON

Classification is performed by a dedicated service after evidence validation and
entity enrichment. Unknown types safely remain GENERAL.
