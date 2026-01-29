---
id: task-002
title: Foundation Setup
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-1, infrastructure]
dependencies: [task-001]
priority: high
---

## Description

Set up the project foundation including directory structure, dependencies, configuration management, and Milvus infrastructure.

**Scope:**
1. Create project directory structure as defined in the implementation plan
2. Create `requirements.txt` with all dependencies
3. Install system dependency: `brew install poppler`
4. Implement `app/core/config.py` with Pydantic settings for:
   - Milvus connection (host, port, collection name)
   - ColQwen2 model configuration
   - Ollama/VLM settings
   - PDF processing settings
   - Retrieval parameters
5. Create `.env.example` template
6. Create `docker-compose.yml` for Milvus (etcd, minio, milvus services)
7. Implement `app/core/milvus_client.py` connection manager
8. Test Milvus connection and collection creation

**Key Files to Create:**
- `requirements.txt`
- `.env.example`
- `docker-compose.yml`
- `app/__init__.py`
- `app/core/__init__.py`
- `app/core/config.py`
- `app/core/milvus_client.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Project directory structure created
- [ ] #2 requirements.txt contains all dependencies
- [ ] #3 Pydantic settings load from .env file
- [ ] #4 docker-compose.yml starts Milvus successfully
- [ ] #5 Milvus client connects and creates collection
- [ ] #6 Collection schema matches plan (patch_id, doc_id, page_number, patch_index, embedding)
<!-- AC:END -->
