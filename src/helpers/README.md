# Helpers

Helper modules provide reusable utilities that can be shared across controllers, models, and routers.

## Files
- `config.py` — Loads environment variables via `pydantic-settings` and exposes a cached `Settings` object through `get_settings()`.

Extend this folder with additional helpers as the project evolves.
