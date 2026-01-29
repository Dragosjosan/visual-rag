---
id: task-002
title: Foundation Setup
status: Done
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-29 11:30'
labels:
  - phase-1
  - infrastructure
dependencies:
  - task-001
priority: high
---

## Description

Set up the project foundation including directory structure, dependencies, configuration management, and Milvus infrastructure.

**Scope:**
1. Create project directory structure as defined in the implementation plan
2. Create `pyproject.toml` with all dependencies (use PyMuPDF for PDF rendering - no system deps needed)
3. Implement `app/core/config.py` with Pydantic settings for:
   - Milvus connection (host, port, collection name)
   - ColQwen2 model configuration
   - Ollama/VLM settings
   - PDF processing settings
   - Retrieval parameters
4. Create `.env.example` template
5. Create `docker-compose.yml` for Milvus (etcd, minio, milvus services)
6. Implement `app/core/milvus_client.py` connection manager
7. Test Milvus connection and collection creation

**Key Files to Create:**
- `pyproject.toml`
- `.env.example`
- `docker-compose.yml`
- `app/__init__.py`
- `app/core/__init__.py`
- `app/core/config.py`
- `app/core/milvus_client.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Project directory structure created
- [x] #2 pyproject.toml contains all dependencies (using uv)
- [x] #3 Pydantic settings load from .env file
- [x] #4 docker-compose.yml starts Milvus successfully
- [x] #5 Milvus client connects and creates collection
- [x] #6 Collection schema matches plan (patch_id, doc_id, page_number, patch_index, embedding)
<!-- AC:END -->
