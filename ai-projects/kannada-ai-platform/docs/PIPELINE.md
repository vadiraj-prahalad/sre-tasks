# Kannada AI Platform – AI Pipeline

Last Updated: 2026-07-07

## Goal

This document explains how a user question moves through the Kannada AI Platform from input to final answer.

## High-Level Flow

```text
User Question
    ↓
Frontend React / PWA
    ↓
FastAPI /ask
    ↓
Conversation Memory
    ↓
Domain Classifier
    ↓
Query Normalizer
    ↓
Alias Resolver
    ↓
Known Answer Store
    ↓
RAG Retrieval
    ↓
Safety Guardrail
    ↓
LLM Fallback
    ↓
Draft Knowledge Queue
    ↓
Confidence Engine
    ↓
Related Topics
    ↓
Feedback Loop
