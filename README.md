# End-to-End Retrieval Augmented Generation (RAG) System

**A production-ready FastAPI microservice for document ingestion, semantic chunking, vector indexing, and retrieval-augmented generation workflows.**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Quick Start](#quick-start)
8. [API Documentation](#api-documentation)
9. [Data Models](#data-models)
10. [LLM Provider Integration](#llm-provider-integration)
11. [Task Queue & Celery](#task-queue--celery)
12. [Vector Database Integration](#vector-database-integration)
13. [Database Migrations](#database-migrations)
14. [Deployment](#deployment)
15. [Monitoring](#monitoring)
16. [Troubleshooting](#troubleshooting)
17. [Contributing](#contributing)
18. [License](#license)

---

## 🎯 Overview

**End-to-End Retrieval Augmented Generation (RAG)** is a comprehensive FastAPI-based microservice designed to facilitate modern AI-powered document processing and retrieval pipelines. The system enables organizations to:

- **Ingest documents** (PDF, TXT) with validation and metadata tracking
- **Process documents** into semantically meaningful chunks with configurable overlap
- **Index embeddings** in vector databases (Qdrant) for semantic search
- **Generate contextual responses** using pluggable LLM providers (Azure OpenAI, Cohere)
- **Monitor workflows** with Celery task queues and asynchronous job processing
- **Persist data** across PostgreSQL, MongoDB, and Redis backends

The system is architected for **scalability**, **observability**, and **production deployment** with support for containerization, health checks, and comprehensive error handling.

---

## ✨ Key Features

### Core Capabilities
- ✅ **Multi-format document support** — PDF and plaintext file ingestion with LangChain loaders
- ✅ **Intelligent chunking** — Recursive character splitting with configurable overlap for downstream RAG applications
- ✅ **Vector embeddings** — Integration with Qdrant vector database for semantic search and retrieval
- ✅ **Pluggable LLM providers** — Support for Azure OpenAI and Cohere with a unified interface
- ✅ **Asynchronous task processing** — Celery workers with RabbitMQ/Redis for long-running jobs
- ✅ **Project-based organization** — Isolate documents and workloads by project identifier
- ✅ **RESTful API** — FastAPI with interactive Swagger documentation and request validation
- ✅ **Monitoring & observability** — Prometheus metrics, Flower dashboard for Celery tasks, and structured logging
- ✅ **Production-ready** — Database migrations (Alembic), health checks, graceful shutdown

### Technical Highlights
- **Async-first architecture** — Built with FastAPI and asyncio for high throughput
- **Type safety** — Full Pydantic validation for requests and configuration
- **Containerized** — Docker Compose setup for all dependencies (PostgreSQL, Qdrant, RabbitMQ, Redis)
- **Enterprise-grade databases** — PostgreSQL with pgvector extension, MongoDB for metadata, Redis for caching/queuing

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │   Data Router    │  │   NLP Router     │  │  Health Router   │     │
│  │ (Upload/Process) │  │ (Index/Generate) │  │  (Status/Metrics)│     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
└────────────────────────────────────────────────────────────────────────┘
         │                      │                        │
         ├──────────────────────┼────────────────────────┤
         │                      │                        │
    ┌────▼────┐          ┌──────▼──────┐         ┌──────▼──────┐
    │ MongoDB  │          │ PostgreSQL  │         │ Redis Cache │
    │ (Assets) │          │ (Chunks)    │         │  (Sessions) │
    └──────────┘          └─────────────┘         └─────────────┘
         │                      │
    ┌────▼──────┐         ┌──────▼───────┐
    │ Qdrant VDB │         │ LLM Providers│
    │ (Vectors)  │         │ (OAI/Cohere) │
    └────────────┘         └──────────────┘
         │
    ┌────▼───────────────────┐
    │  Celery Task Queue      │
    │ (RabbitMQ Broker)       │
    │ - Email Reports         │
    │ - File Processing       │
    │ - Data Indexing         │
    └────────────────────────┘
```

---

## 📋 Prerequisites

### System Requirements
- **Python:** 3.10 or later
- **Operating System:** Windows, macOS, or Linux
- **Disk Space:** Minimum 2GB (for dependencies and sample data)
- **RAM:** Minimum 4GB recommended for local development with containerized services

### Required Services
- **PostgreSQL** 13+ with pgvector extension (for chunk embeddings)
- **MongoDB** 7.x (for asset and project metadata)
- **Qdrant** 1.x (for vector similarity search)
- **RabbitMQ** (for Celery task queue) or Redis (for alternative broker)
- **Redis** (for Celery result backend and caching)

### Optional API Keys
- **Azure OpenAI:** For GPT-4 and embedding models
- **Cohere API:** For alternative generation and embedding models

### Development Tools
- **Docker Desktop** (for containerized service stack)
- **Git** (for version control)
- **curl** or **Postman** (for API testing)

---

## 🚀 Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/sam1o1/eoe-rag.git
cd eoe-rag
```

### Step 2: Create Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r src/requirements.txt
```

### Step 4: Start Docker Services (Recommended)
```bash
docker compose -f docker/docker-compose.yml up -d
```

This will spin up:
- PostgreSQL (pgvector)
- MongoDB
- Qdrant
- RabbitMQ
- Redis
- Prometheus & Grafana (monitoring)
- Nginx (reverse proxy)

### Step 5: Run Database Migrations
```bash
cd src
alembic upgrade head
cd ..
```

---

## ⚙️ Configuration

### Environment File Setup

Create a `.env` file in the project root by copying the example:
```bash
cp .env.example .env
```

### Core Configuration Variables

#### Application
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | str | `"End-to-End RAG"` | Application display name |
| `APP_VERSION` | str | `"1.0.0"` | Semantic version |
| `DEBUG` | bool | `False` | Enable FastAPI debug mode |
| `PRIMARY_LANG` | str | `"en"` | Primary language for templates |
| `DEFAULT_LANG` | str | `"en"` | Default fallback language |

#### File Handling
| Variable | Type | Description |
|----------|------|-------------|
| `ALLOWED_FILE_TYPES` | list | Allowed MIME types (e.g., `["application/pdf", "text/plain"]`) |
| `ALLOWED_MAX_FILE_SIZE` | int | Max file size in bytes (default: 50MB) |
| `FILE_DEFAULT_CHUNK_SIZE` | int | Default chunk size for text splitting (default: 512) |

#### PostgreSQL
| Variable | Required | Description |
|----------|----------|-------------|
| `POSTGRES_HOST` | ✓ | Hostname (default: `localhost`) |
| `POSTGRES_PORT` | ✓ | Port (default: `5432`) |
| `POSTGRES_USERNAME` | ✓ | Database user |
| `POSTGRES_PASSWORD` | ✓ | Database password |
| `POSTGRES_MAIN_DB` | ✓ | Main database name |

#### MongoDB
| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | ✓ | Connection string |
| `MONGO_DB_NAME` | ✓ | Database name |
| `MONGO_INITDB_ROOT_USERNAME` | ✓ | Root user |
| `MONGO_INITDB_ROOT_PASSWORD` | ✓ | Root password |

#### Vector Database (Qdrant)
| Variable | Description |
|----------|-------------|
| `QDRANT_HOST` | Qdrant server hostname (default: `localhost`) |
| `QDRANT_PORT` | Qdrant server port (default: `6334`) |
| `QDRANT_URL` | Full Qdrant server URL (e.g., `http://qdrant:6333`) |
| `VECTOR_DB_BACKEND` | Provider type (e.g., `QDRANT`) |

#### LLM Providers

**Azure OpenAI:**
```env
GENERATION_BACKEND=OPENAI
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_GPT4O=gpt-4o
AZURE_OPENAI_DEPLOYMENT_EMBEDDINGS=text-embedding-3-small
EMBEDDING_BACKEND=OPENAI
EMBEDDING_MODEL_ID=text-embedding-3-small
EMBEDDING_MODEL_SIZE=1536
GENERATION_MOELL_ID=gpt-4o
```

**Cohere:**
```env
GENERATION_BACKEND=COHERE
COHERE_API_KEY=<your-api-key>
EMBEDDING_BACKEND=COHERE
EMBEDDING_MODEL_ID=embed-english-v3.0
EMBEDDING_MODEL_SIZE=1024
GENERATION_MOELL_ID=command
```

#### Celery & Task Queue
| Variable | Description |
|----------|-------------|
| `CELERY_BROKER_URL` | RabbitMQ/Redis broker (e.g., `amqp://guest:guest@localhost:5672//`) |
| `CELERY_RESULT_BACKEND` | Result backend (e.g., `redis://localhost:6379/0`) |
| `CELERY_TASK_SERIALIZER` | Serialization format (default: `json`) |
| `CELERY_TASK_ACKS_LATE` | Task acknowledgment strategy (default: `True`) |
| `CELERY_TASK_TIME_LIMIT` | Task timeout in seconds (default: `3600`) |
| `CELERY_WORKER_CONCURRENCY` | Number of concurrent workers (default: `4`) |

### Example `.env` File
```env
# Application
APP_NAME=End-to-End RAG Service
APP_VERSION=1.0.0
DEBUG=False
PRIMARY_LANG=en
DEFAULT_LANG=en

# File Handling
ALLOWED_FILE_TYPES=["application/pdf", "text/plain"]
ALLOWED_MAX_FILE_SIZE=52428800
FILE_DEFAULT_CHUNK_SIZE=512

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=admin
POSTGRES_MAIN_DB=rag_db

# MongoDB
MONGO_URI=mongodb://admin:adminpassword@localhost:27017
MONGO_DB_NAME=rag_db
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=adminpassword

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6334
QDRANT_URL=http://qdrant:6333
VECTOR_DB_BACKEND=QDRANT

# Azure OpenAI
GENERATION_BACKEND=OPENAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_GPT4O=gpt-4o
AZURE_OPENAI_DEPLOYMENT_EMBEDDINGS=text-embedding-3-small
EMBEDDING_BACKEND=OPENAI
EMBEDDING_MODEL_ID=text-embedding-3-small
EMBEDDING_MODEL_SIZE=1536
GENERATION_MOELL_ID=gpt-4o

# Celery
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_TASK_ACKS_LATE=True
CELERY_TASK_TIME_LIMIT=3600
CELERY_WORKER_CONCURRENCY=4
```

---

## ⚡ Quick Start

### 1. Start Services
```bash
# Terminal 1: Start all Docker services
docker compose -f docker/docker-compose.yml up -d

# Verify services are running
docker compose -f docker/docker-compose.yml ps
```

### 2. Run Database Migrations
```bash
cd src
alembic upgrade head
cd ..
```

### 3. Start FastAPI Server
```bash
# Terminal 2: Start the API server
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 4. Start Celery Worker
```bash
# Terminal 3: Start Celery worker
cd src
python -m celery -A celery_app worker -l info -P threads -c 4 -Q default,email_reports,file_processing,data_indexing
```

### 5. (Optional) Start Flower Dashboard
```bash
# Terminal 4: Monitor tasks
cd src
celery -A celery_app flower --conf=flowerconfig.py
# Open http://localhost:5555
```

### 6. Test the API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload a file
curl -X POST "http://localhost:8000/api/v1/data/upload/project-1" \
     -F "file=@/path/to/document.pdf"

# View API documentation
# Open http://localhost:8000/docs in your browser
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Health & Status Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "app_name": "End-to-End RAG Service",
  "version": "1.0.0"
}
```

---

### Data Ingestion Endpoints

#### Upload File
```http
POST /data/upload/{project_id}
Content-Type: multipart/form-data

file: <binary>
```

**Parameters:**
- `project_id` (path, required): Unique project identifier

**Response:**
```json
{
  "file_id": "abc123_document.pdf",
  "file_name": "document.pdf",
  "file_type": "application/pdf",
  "file_size_mb": 2.5,
  "status": "uploaded",
  "message": "File uploaded successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/data/upload/my-project" \
     -F "file=@research_paper.pdf"
```

---

#### Process File
```http
POST /data/process/{project_id}
Content-Type: application/json

{
  "file_id": "abc123_document.pdf",
  "chunk_size": 512,
  "overlap_size": 50,
  "do_reset": 0
}
```

**Response:**
```json
{
  "project_id": "my-project",
  "file_id": "abc123_document.pdf",
  "chunks_created": 45,
  "total_tokens": 12500,
  "status": "processed"
}
```

---

### NLP & Retrieval Endpoints

#### Index Project into Vector DB
```http
POST /nlp/index/push/{project_id}
Content-Type: application/json

{
  "do_reset": 0
}
```

**Response:**
```json
{
  "status": "indexed",
  "project_id": "my-project",
  "inserted_items_count": 45
}
```

---

#### Get Collection Info
```http
GET /nlp/index/info/{project_id}
```

**Response:**
```json
{
  "collection_info": {
    "name": "project_my-project",
    "points_count": 45,
    "vectors_count": 45
  }
}
```

---

## 📊 Data Models

### Project Structure
```
src/
├── controllers/          # Business logic orchestration
├── models/              # Data persistence & schemas
│   ├── db_schemas/      # PostgreSQL/MongoDB schema definitions
│   │   └── rag/         # RAG-specific schemas with Alembic migrations
│   └── enums/           # Enumeration types
├── routers/             # FastAPI endpoint definitions
│   └── schemas/         # Request/response Pydantic models
├── stores/              # Data layer (LLM, Vector DB)
│   ├── llm/            # LLM provider factory & clients
│   └── vectordb/       # Vector database clients
├── tasks/              # Celery async task definitions
├── utils/              # Utility functions & helpers
└── main.py             # FastAPI application entry point
```

---

## 🤖 LLM Provider Integration

### Supported Providers

#### Azure OpenAI
- **Models:** GPT-4, GPT-4o, GPT-4-Turbo, text-embedding-3-large, text-embedding-3-small
- **Capabilities:** Generation, embedding, prompt templates
- **Configuration:** API endpoint, API key, deployment names

#### Cohere
- **Models:** command, command-light, embed-english-v3.0
- **Capabilities:** Generation, embedding, result streaming
- **Configuration:** API key, model selection

---

## 🔄 Task Queue & Celery

### Registered Tasks
- **send_email_report** — Queue: `email_reports`
- **process_project_files** — Queue: `file_processing`
- **data_indexing** — Queue: `data_indexing`

### Start Worker
```bash
cd src
python -m celery -A celery_app worker -l info -P threads -c 4
```

### Monitor with Flower
```bash
cd src
celery -A celery_app flower
# Open http://localhost:5555
```

---

## 🗂️ Vector Database Integration

### Qdrant
- **Port:** 6333 (API), 6334 (gRPC)
- **Collections:** Named as `project_{project_id}`
- **Vector Dimension:** 1536 (for text-embedding-3-small)
- **Metric:** Cosine similarity

### REST API Examples
```bash
# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/project_my-project

# Delete collection
curl -X DELETE http://localhost:6333/collections/project_my-project
```

---

## 🔧 Database Migrations

### Using Alembic
```bash
# Create migration
cd src/models/db_schemas/rag
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1

# View history
alembic history
```

---

## 🚢 Deployment

### Docker Compose
```bash
# Start all services
docker compose -f docker/docker-compose.yml up -d --build

# View logs
docker compose -f docker/docker-compose.yml logs -f fastapi

# Stop services
docker compose -f docker/docker-compose.yml down
```

### Services & Ports
| Service | Port | URL |
|---------|------|-----|
| FastAPI | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | — |
| MongoDB | 27017 | — |
| Qdrant | 6333/6334 | http://localhost:6333 |
| RabbitMQ | 5672 | amqp://localhost:5672 |
| Redis | 6379 | — |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |
| Flower | 5555 | http://localhost:5555 |

---

## 📈 Monitoring

### Prometheus Metrics
Access metrics at: `http://localhost:9000/metrics`

### Grafana Dashboards
- URL: `http://localhost:3000`
- Default credentials: `admin` / `admin`

### Flower Task Monitoring
- URL: `http://localhost:5555`
- Real-time task execution, worker status, and performance metrics

---

## 🐛 Troubleshooting

### FastAPI Won't Start
```bash
# Set Python path
export PYTHONPATH=src
uvicorn main:app --reload
```

### MongoDB Connection Failed
```bash
# Verify credentials
docker compose exec mongodb mongosh -u admin -p --authenticationDatabase admin
```

### Qdrant Storage Lock
Use Qdrant server mode (Docker) instead of embedded:
```env
QDRANT_URL=http://qdrant:6333
```

### Redis Authentication Error
```bash
# Verify credentials in CELERY_RESULT_BACKEND
redis-cli -h localhost -p 6379 ping
```

### PostgreSQL Migration Failed
```bash
# Check if service is running
docker compose ps | grep postgres

# Test connection
psql -h localhost -U postgres -d rag_db
```

---

## 🤝 Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Run linting: `black src/ && flake8 src/`
4. Commit changes: `git commit -am 'Add feature'`
5. Push and create pull request

### Code Style
- **Formatter:** Black
- **Linter:** Flake8
- **Type Hints:** Full type annotations required
- **Docstrings:** Google-style docstrings for all functions

---

## 📄 License

This project is licensed under the **MIT License**. See [`LICENSE`](LICENSE) file for details.

---

## 📞 Support & Resources

- **API Documentation:** [Swagger UI](http://localhost:8000/docs)
- **Issues:** [GitHub Issues](https://github.com/sam1o1/eoe-rag/issues)
- **Repository:** [sam1o1/eoe-rag](https://github.com/sam1o1/eoe-rag)

---

**Last Updated:** December 8, 2025  
**Maintained by:** Sam1o1 / EOE Contributors

---

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
