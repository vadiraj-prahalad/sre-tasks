# Engineering Decisions - Kannada AI Platform

## Purpose

This document explains why each script/service exists, what problem it solved, and how the architecture evolved.

---

## manage.py

### Problem
The project had many operational commands:

- ingest sources
- generate embeddings
- list documents
- evaluate RAG

Remembering long module commands was becoming difficult.

### Decision
Created `backend/manage.py` as a single command runner.

### Benefit
Simplifies operations:

```bash
python manage.py list
python manage.py sync
python manage.py evaluate
