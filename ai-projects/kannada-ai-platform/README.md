# Kannada AI Platform

A Kannada-first AI knowledge platform built with FastAPI, trusted knowledge lookup, query normalization, and local LLM fallback using Ollama.

## Current Features

- FastAPI backend
- `/health` endpoint
- `/ask` endpoint
- Trusted Kannada knowledge base
- Query normalization for English/Kanglish inputs
- Local LLM fallback using Ollama
- Repository layer for knowledge data
- Config layer for LLM settings

## Architecture

```text
User
 ↓
FastAPI API Layer
 ↓
Router Layer
 ↓
Query Normalizer
 ↓
Knowledge Service
 ↓
Knowledge Repository
 ↓
Kannada JSON Knowledge Base

Fallback:
Router
 ↓
Local LLM Client
 ↓
Ollama / Llama3
