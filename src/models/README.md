# Data Models

The `models/` package implements persistence concerns for Mini RAG using Motor (async PyMongo) and Pydantic schemas.

## Components
- `BaseDataModel.py` — Base class that wires application settings and MongoDB clients.
- `PorjectDataModel.py` — Handles project lifecycle operations (create, list, fetch or create).
- `AssetsDataModel.py` — Persists metadata about uploaded files and retrieves project assets.
- `ChunkDataModel.py` — Stores text chunks resulting from document processing.
- `db_schemas/` — Pydantic models mirroring MongoDB documents and index definitions.
- `enums/` — Enumerations for collection names, file extensions, and response signals.

Models are designed to be instantiated with the FastAPI app's shared Motor client for efficient reuse.
