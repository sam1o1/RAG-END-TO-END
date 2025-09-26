# Application Source

The `src/` directory hosts the FastAPI application, domain logic, and supporting assets for Mini RAG.

## Key Modules
- `main.py` — FastAPI entry point that wires routers and MongoDB connections.
- `routers/` — HTTP routers that expose health, file upload, and processing endpoints.
- `controllers/` — Orchestrates file handling, chunking, and project management tasks.
- `models/` — Data access layer, schema definitions, and enums for MongoDB collections.
- `helpers/` — Shared utilities such as environment configuration loading.
- `assets/` — On-disk storage for uploaded documents grouped by project identifier.

## Running the App
Ensure `PYTHONPATH` includes `src` when starting Uvicorn:
```bash
uvicorn main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

Refer to subdirectory READMEs for deeper details on each module.
