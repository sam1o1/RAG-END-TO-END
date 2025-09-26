# Assets

The `assets/` directory stores files that support runtime behaviors.

## Structure
- `files/` — Holds uploaded documents segregated by project identifier. Each project receives its own subdirectory managed by `ProjectController`.

## Notes
- Ensure the application process has write permissions to this directory.
- Uploaded content is not version controlled by default; consider cleaning the folder for long-running environments.
