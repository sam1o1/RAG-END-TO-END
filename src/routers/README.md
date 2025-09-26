# Routers

This package defines FastAPI routers that expose HTTP endpoints for Mini RAG.

## Modules
- `base.py` — Health endpoint (`/api/v1/health`) reporting application metadata.
- `data.py` — Uploads files, triggers document processing, and persists chunk results.
- `schemas/` — Request payload definitions shared across router functions.

Routers are registered in `main.py` to compose the FastAPI application.
