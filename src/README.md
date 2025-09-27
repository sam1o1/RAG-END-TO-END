# Application Source

The `src/` directory hosts the FastAPI application, domain logic, and supporting assets for Mini RAG.

## Key Modules
- `main.py` — FastAPI entry point that wires routers, MongoDB, and LLM providers.
- `routers/` — HTTP routers that expose health, file upload, and processing endpoints.
- `controllers/` — Orchestrates file handling, chunking, and project management tasks.
- `models/` — Data access layer, schema definitions, and enums for MongoDB collections.
- `helpers/` — Shared utilities such as environment configuration loading.
- `assets/` — On-disk storage for uploaded documents grouped by project identifier.
- `stores/` — LLM provider interfaces, factory, and concrete client implementations.
- `requirements.txt` — Python dependency lock-list for the service.

Refer to subdirectory READMEs for deeper details on each module.
