---
id: task-012
title: Docker Deployment
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-5, infrastructure, docker]
dependencies: [task-011]
priority: medium
---

## Description

Finalize Docker Compose configuration for full stack deployment and create the application Dockerfile.

**Scope:**
1. Create `Dockerfile` for the FastAPI application:
   - Base: python:3.11-slim
   - Install poppler-utils
   - Install Python dependencies
   - Copy application code
   - Run uvicorn

2. Update `docker-compose.yml`:
   - Add app service
   - Configure volumes for data persistence
   - Set environment variables
   - Configure health checks
   - Network configuration

3. Create deployment documentation:
   - Update README.md with setup instructions
   - Document Ollama setup (runs on host)
   - Environment variable reference

**Docker Services:**
- etcd: Milvus metadata store
- minio: Milvus object storage
- milvus: Vector database (ports 19530, 9091)
- app: FastAPI application (port 8000)

**Note:** Ollama runs on host for Metal acceleration:
```bash
brew install ollama
ollama pull qwen2-vl:7b
ollama serve
```

**Key Files to Create/Update:**
- `Dockerfile`
- `docker-compose.yml` (update with app service)
- `README.md`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dockerfile builds successfully
- [ ] #2 docker-compose up starts all services
- [ ] #3 App container connects to Milvus
- [ ] #4 App container connects to Ollama on host
- [ ] #5 Health checks pass for all services
- [ ] #6 Data persists across container restarts
- [ ] #7 README documents full setup process
<!-- AC:END -->
