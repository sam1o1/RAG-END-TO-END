# Controllers

Controller classes encapsulate application-specific orchestration that sits between HTTP routers and lower-level services.

## Modules
- `BaseController.py` — Provides shared configuration access and filesystem helpers.
- `ProjectController.py` — Ensures on-disk project directories exist and manages storage paths.
- `DataController.py` — Validates uploads and generates unique filenames for incoming assets.
- `ProcessController.py` — Loads stored files via LangChain loaders and produces text chunks for persistence.

Controllers are invoked by routers to keep endpoint functions tidy while reusing shared logic.
