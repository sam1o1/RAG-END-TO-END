# Database Schemas

Pydantic models in this folder describe the MongoDB documents persisted by Mini RAG.
They also enumerate the indexes that each collection requires on first use.

## Schemas
- `project.py` — Represents a project record keyed by `project_id`.
- `asset.py` — Captures metadata for an uploaded file, including size, type, and associated project.
- `data_chunk.py` — Stores generated text chunk content, metadata, and order information.

Each schema exposes a `get_indexes()` helper consumed by the data models to provision indexes during startup.
