# Docker Resources

This directory contains the container orchestration assets used to run the Mini RAG service dependencies locally.

## Contents
- `docker-compose.yml` — spins up a MongoDB 7.x instance bound to `localhost:27017`.
- `mongodb/` — default Docker volume mount that persists MongoDB data between container restarts.

## Usage
1. Set the MongoDB credentials in the project-level `.env` file (`MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD`).
2. From the repository root run:
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```
3. Stop the stack with `docker compose -f docker/docker-compose.yml down` when finished.

## Notes
- The `mongodb/` folder mirrors MongoDB's internal storage format; do not edit its contents manually.
- Clean up the persisted data by removing the Docker volume: `docker volume rm docker_mongodb`.
