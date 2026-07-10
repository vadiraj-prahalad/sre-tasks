# Developer Guide

## Setup

Create virtual environment

Install dependencies

Run backend

Run frontend

## Knowledge Commands

python -m app.db.tools.ingest_all_sources

python -m app.db.tools.generate_chunk_embeddings

python manage.py evaluate

## Development Flow

Edit

Evaluate

Commit

Push


---

# Decision: Separate Evidence Collection from Editorial Generation

## Date

2026-07-10

## Problem

Initially the editorial pipeline directly consumed raw provider responses.

This tightly coupled:

- Internet providers
- Evidence filtering
- Editorial prompting

Adding new providers or validating evidence would require modifying multiple services.

## Decision

Split the pipeline into independent stages.

Internet Providers
↓

Evidence Quality

↓

Evidence Builder

↓

Conflict Detection

↓

Editorial Prompt

↓

GPT-5.5

↓

Draft Queue

## Benefits

- Easier to extend
- Better testing
- Cleaner architecture
- Easier debugging
- Supports future providers

## Future

This architecture allows adding Britannica, government datasets or Kannada encyclopedias without changing the editorial workflow.

## Interview Explanation

This follows the Single Responsibility Principle.

Each service performs one job:

- Providers fetch.
- Quality filters.
- Builder normalizes.
- Conflict detector validates.
- Editorial AI writes.
