# Mini RAG Service

Mini RAG is a FastAPI-based microservice that ingests plain text and PDF documents, stores their metadata in MongoDB, and prepares retrieval-ready chunks with LangChain utilities. It now also wires pluggable LLM providers so generation and embedding calls can be delegated to Azure OpenAI or Cohere with a shared interface.

## Features
- File upload endpoint with size and MIME type validation.
- Persistent project and asset tracking in MongoDB collections.
- Text extraction for `.txt` and `.pdf` files using LangChain loaders.
- Configurable recursive chunking with overlap control for downstream RAG pipelines.
- Pluggable LLM connectors (Azure OpenAI or Cohere) for generation and embedding workloads.

## Project Structure
```
mini_rag_eslam/
├─ docker/                # MongoDB docker-compose definition and volume data
├─ src/
│  ├─ assets/files/       # Uploaded source files grouped by project id
│  ├─ controllers/        # Request orchestration and file processing logic
│  ├─ helpers/config.py   # Pydantic-based settings loader
│  ├─ models/             # MongoDB data access layer and schemas
│  ├─ routers/            # FastAPI routers for health and data endpoints
│  ├─ stores/llm/         # Provider factory and clients for LLM generation/embeddings
│  └─ main.py             # FastAPI application entry point
├─ .env.example           # Environment variable template
└─ README.md
```

## Directory Guides
- [docker](docker/README.md) — Compose stack and volume layout.
- [docker/mongodb](docker/mongodb/README.md) — MongoDB volume guidance.
- [src](src/README.md) — Application entry point and module map.
- [src/assets](src/assets/README.md) — Uploaded document storage.
- [src/assets/files](src/assets/files/README.md) — Project-specific file directories.
- [src/controllers](src/controllers/README.md) — Orchestration logic for uploads and processing.
- [src/helpers](src/helpers/README.md) — Shared utilities and configuration.
- [src/models](src/models/README.md) — Data access layer and persistence types.
- [src/models/db_schemas](src/models/db_schemas/README.md) — Pydantic schemas and index definitions.
- [src/models/enums](src/models/enums/README.md) — Enumerations referenced across modules.
- [src/routers](src/routers/README.md) — FastAPI endpoint registrations.
- [src/routers/schemas](src/routers/schemas/README.md) — Request payload definitions.
- [src/stores](src/stores/README.md) — LLM clients and provider plumbing.
- [src/stores/llm](src/stores/llm/README.md) — Factory, enums, and provider contracts.

## Prerequisites
- Python 3.10 or later.
- MongoDB 7.x (local instance or Docker container).
- `pip` for dependency management.
- Optional: Docker Desktop for running MongoDB via `docker-compose`.
- Optional: Azure OpenAI and/or Cohere credentials when exercising LLM-backed features.

## Setup
1. **Clone and create a virtual environment**
   ```bash
   git clone <repo-url>
   cd mini_rag_eslam
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r src/requirements.txt
   ```
3. **Environment configuration**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with values that match your environment.

### Environment Variables
#### Core service
- `APP_NAME`, `APP_VERSION`, `DEBUG`
- `ALLOWED_FILE_TYPES`, `ALLOWED_MAX_FILE_SIZE`, `FILE_DEFAULT_CHUNK_SIZE`

#### MongoDB
- `MONGO_URI`, `MONGO_DB_NAME`
- `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` (required when using the provided MongoDB compose stack)

#### LLM providers (optional)
- `GENERATION_BACKEND`, `EMBEDDING_BACKEND` — set to `OPENAI` (Azure OpenAI) or `COHERE` for the respective factory outputs. The sample `.env` ships with placeholder strings; update them to the enum values before running.
- Azure OpenAI: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT_GPT4O`, `AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI`, `AZURE_OPENAI_DEPLOYMENT_EMBEDDINGS`.
- Cohere: `CHHERE_API_KEY` (note the current spelling in `Settings`).
- Shared defaults: `GENERATION_MOELL_ID`, `EMBEDDING_MODEL_ID`, `EMBEDDING_MODEL_SIZE`, `INPUT_DEFAULT_MAX_CHARS`, `GENERATION_DEFAULT_MAX_TOKENS`, `GENERATION_DEFAULT_TEMPERATURE`.

## Running MongoDB with Docker (optional)
```bash
docker compose -f docker/docker-compose.yml up -d
```
The compose file exposes MongoDB on `27017` and persists data to a named Docker volume. Provide the root username and password via your `.env` file before starting the container.

## Starting the API
Activate your virtual environment, ensure MongoDB is reachable, then launch FastAPI with Uvicorn.

From the project root:
```bash
export PYTHONPATH=src   # PowerShell: $env:PYTHONPATH = "src"
uvicorn main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```
The API is served at `http://localhost:8000`. Interactive documentation is exposed at `/docs` (Swagger UI) and `/redoc`.

## API Overview

### Health Check
- **Endpoint:** `GET /api/v1/health`
- **Response:** basic service status, app name, and version from settings.

### Upload File
- **Endpoint:** `POST /api/v1/data/upload/{project_id}`
- **Body:** `multipart/form-data` with a single `file` field.
- **Behavior:**
  - Verifies MIME type and file size against configured limits.
  - Stores the uploaded file in `src/assets/files/{project_id}`.
  - Creates a MongoDB asset record linked to the project.
- **Sample cURL:**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/data/upload/demo-project" \
       -F "file=@/path/to/document.pdf"
  ```
- **Response fields:** `file_name`, `file_type`, `file_size` (MB), `file_id` for subsequent processing.

### Process File
- **Endpoint:** `POST /api/v1/data/process/{project_id}`
- **Body:** JSON matching the schema below.
  ```json
  {
    "file_id": "<value returned by upload>",
    "chunk_size": 512,
    "overlap_size": 50,
    "do_reset": 1
  }
  ```
- **Behavior:**
  - Loads the stored file via LangChain (`TextLoader` or `PyMuPDFLoader`).
  - Splits content into overlapping chunks with `RecursiveCharacterTextSplitter`.
  - Optionally deletes existing chunks for the project when `do_reset` is `1`.
  - Persists chunk metadata and text in the `chunks` MongoDB collection.
- **Sample cURL:**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/data/process/demo-project" \
       -H "Content-Type: application/json" \
       -d '{
             "file_id": "abc123_document.pdf",
             "chunk_size": 512,
             "overlap_size": 50,
             "do_reset": 1
           }'
  ```

## LLM Provider Configuration
- The FastAPI startup hook instantiates `app.generation_client` and `app.embedding_client` via `LLMProviderFactory`.
- Use `GENERATION_BACKEND`/`EMBEDDING_BACKEND` to choose the provider (`OPENAI` for Azure OpenAI, `COHERE` for Cohere).
- Set model identifiers (`GENERATION_MOELL_ID`, `EMBEDDING_MODEL_ID`) and optional defaults for token limits or temperature.
- Provider clients expose `generate_text()` and `embed_text()` and can be injected into future endpoints for downstream RAG flows.

## Data Model
- **Projects (`projects` collection):** tracks unique project identifiers.
- **Assets (`assets` collection):** metadata describing uploaded files.
- **Chunks (`chunks` collection):** text segments generated during processing.

Uploaded files live on disk under `src/assets/files/{project_id}`. Ensure the application has write access to this directory.

## Development Notes
- Configuration is powered by `pydantic-settings`; values are loaded from `.env` at startup.
- Async Motor client connections are created and terminated through FastAPI startup/shutdown events.
- Supported content types are controlled through `ALLOWED_FILE_TYPES`; adjust to add loaders for additional formats.
- Chunking defaults (`chunk_size`, `overlap_size`) can be tuned per request without restarting the service.
- LLM providers share a lightweight interface so new providers can be registered in `src/stores/llm/providers/`.

## Troubleshooting
- **Validation errors during upload:** verify MIME type and file size, and confirm `ALLOWED_FILE_TYPES`/`ALLOWED_MAX_FILE_SIZE` values.
- **MongoDB connection errors:** double-check `MONGO_URI`, credentials, and that MongoDB is running.
- **LLM client is `None`:** confirm `GENERATION_BACKEND`/`EMBEDDING_BACKEND` match the expected enum values and that required API keys are present.
- **Import errors when starting Uvicorn:** ensure `PYTHONPATH` includes `src` or launch with `uvicorn main:app --app-dir src` as shown above.

## License
This project is distributed under the terms of the [MIT License](LICENSE).
