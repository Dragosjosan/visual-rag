---
id: task-011
title: FastAPI Backend
status: Done
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-31 14:18'
labels:
  - phase-5
  - api
dependencies:
  - task-006
  - task-008
  - task-010
priority: medium
---

## Description

Implement the FastAPI backend that exposes the Visual RAG functionality via REST API endpoints.

**Scope:**
1. Implement `app/models/schemas.py`:
   - Request/response Pydantic models
   - IngestRequest, IngestResponse
   - SearchRequest, SearchResponse
   - GenerateRequest, GenerateResponse

2. Implement API endpoints in `app/api/v1/`:
   - `ingest.py` - POST /api/v1/ingest
   - `search.py` - POST /api/v1/search
   - `generate.py` - POST /api/v1/generate

3. Implement `app/main.py`:
   - FastAPI application
   - Lifespan handlers for model loading/cleanup
   - CORS middleware
   - Health check endpoint

**API Endpoints:**

```
POST /api/v1/ingest
Body: { "pdf_path": "data/pdfs/doc.pdf", "doc_id": "optional" }
Response: { "doc_id": "abc123", "pages": 26, "patches": 26624 }

POST /api/v1/search
Body: { "query": "MaxSim formula", "top_k": 5 }
Response: { "results": [{ "doc_id": "...", "page": 6, "score": 42.3 }] }

POST /api/v1/generate
Body: { "query": "What is ColPali?", "top_k": 3 }
Response: { "answer": "...", "sources": [...] }

GET /health
Response: { "status": "healthy", "milvus": true, "model": true }
```

**Key Files to Create:**
- `app/models/__init__.py`
- `app/models/schemas.py`
- `app/api/__init__.py`
- `app/api/v1/__init__.py`
- `app/api/v1/router.py`
- `app/api/v1/ingest.py`
- `app/api/v1/search.py`
- `app/api/v1/generate.py`
- `app/api/dependencies.py`
- `app/main.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 FastAPI app starts without errors
- [ ] #2 /health endpoint returns healthy status
- [ ] #3 /api/v1/ingest accepts PDF and indexes it
- [ ] #4 /api/v1/search returns ranked results
- [ ] #5 /api/v1/generate returns RAG answer
- [ ] #6 CORS enabled for cross-origin requests
- [ ] #7 API documentation available at /docs
<!-- AC:END -->
