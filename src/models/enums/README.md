# Enumerations

Enumerations centralize cross-cutting constants used throughout Mini RAG.

## Files
- `DataBaseEnum.py` — Collection names for MongoDB persistence.
- `ProcessEnum.py` — Supported file extensions for document processing.
- `ResponseEnums.py` — User-facing response messages shared by controllers and routers.

Import enums from `models` to avoid tight coupling with nested package paths.
