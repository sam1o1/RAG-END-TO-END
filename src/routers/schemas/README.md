# Router Schemas

This module houses Pydantic request payloads consumed by router endpoints.

## Files
- `data.py` — Defines `ProcessRequest`, the body expected by `/api/v1/data/process/{project_id}`.

Add new schema modules here as additional endpoints require structured input validation.
