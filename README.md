# Mini RAG Service

Mini RAG is a FastAPI-based microservice that ingests plain text and PDF documents, stores their metadata in MongoDB, and prepares retrieval-ready chunks using LangChain utilities. It is designed as a lightweight foundation for retrieval-augmented generation (RAG) workflows.

## Features
- File upload endpoint with size and MIME type validation.
- Persistent project and asset tracking in MongoDB collections.
- Text extraction for `.txt` and `.pdf` files using LangChain loaders.
- Configurable recursive chunking with overlap control for downstream RAG pipelines.
- Async I/O throughout the data path for efficient large-file handling.

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
│  └─ main.py             # FastAPI application entry point
├─ .env.example           # Environment variable template
└─ README.md
```

## Prerequisites
- Python 3.10 or later
- MongoDB 7.x (local instance or Docker container)
- `pip` for dependency management
- Optional: Docker Desktop for running MongoDB via `docker-compose`

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
   Update `.env` with values that match your environment:
   - `APP_NAME`, `APP_VERSION`, `DEBUG`
   - `ALLOWED_FILE_TYPES`, `ALLOWED_MAX_FILE_SIZE`, `FILE_DEFAULT_CHUNK_SIZE`
   - `MONGO_URI`, `MONGO_DB_NAME`
   - `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` (required when using the bundled MongoDB container)

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
The API will be available at `http://localhost:8000`. Interactive documentation is exposed at `/docs` (Swagger UI) and `/redoc`.

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

## Troubleshooting
- **Validation errors during upload:** verify MIME type and file size, and confirm `ALLOWED_FILE_TYPES`/`ALLOWED_MAX_FILE_SIZE` values.
- **MongoDB connection errors:** double-check `MONGO_URI`, credentials, and that MongoDB is running.
- **Import errors when starting Uvicorn:** ensure `PYTHONPATH` includes `src` or launch with `uvicorn main:app --app-dir src` as shown above.

## License
This project is distributed under the terms of the [MIT License](LICENSE).
