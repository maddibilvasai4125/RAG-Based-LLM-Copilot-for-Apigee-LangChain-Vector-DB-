# Apigee-LLM (Phase 1) — Fresh Start

Goal: A free, local RAG assistant that answers Apigee questions from official docs, with citations.

Runbook (high-level):
1) Ingest docs  → clean Markdown
2) Chunk notes  → overlapping pieces
3) Index        → embeddings + vector DB
4) Ask          → retrieve + rerank + LLM (with sources)
5) API + Web    → share it in a simple UI

This README will grow as we complete each chunk.