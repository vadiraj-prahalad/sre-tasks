
# Interview Topic — Deterministic Entity Classification

## Question

How did you classify knowledge entities without relying on an LLM?

## Answer

I used Wikidata's structured P31 instance-of property as the primary signal.

For example, Kempe Gowda I resolves to Wikidata entity Q6387049. Its P31 claim
contains Q5, which represents a human. A dedicated classification service maps
Q5 to the platform entity type PERSON.

The Wikidata provider only retrieves and normalizes facts. It does not contain
platform business mappings. The classification service interprets those facts
and returns a new immutable KnowledgeEntity.

## Why Not Put Classification in the Provider?

Providers should remain responsible for external integration.

Platform taxonomy is domain logic.

Separating them provides:

- lower coupling;
- independent testing;
- easier provider replacement;
- reusable provider output;
- independent evolution of the platform taxonomy.

## Why Not Use Description Keywords?

Description-based classification is language-dependent and unreliable.

Examples such as ruler, founder, saint, poet, or historical figure may all refer
to a person but require many fragile rules.

Structured ontology IDs are more deterministic and auditable.

## Why Preserve GENERAL?

Unknown or unsupported Wikidata types must not be guessed.

GENERAL is a safe fallback that allows the pipeline to continue without
inventing semantic meaning.

## Design Patterns

- Strategy-style classification service
- Mapping registry
- Immutable value object replacement
- Anti-corruption layer around external provider data
- Separation of concerns
- Fail-safe default

## Senior-Level Discussion

The classifier currently supports exact P31 mappings.

Future extensions may support:

- multiple P31 values;
- precedence rules;
- P279 subclass traversal;
- confidence and provenance;
- conflicting type resolution;
- versioned taxonomy;
- editorial overrides.
