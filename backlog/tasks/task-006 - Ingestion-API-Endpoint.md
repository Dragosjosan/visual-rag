---
id: task-006
title: Ingestion API Endpoint
status: Done
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-29 20:07'
labels:
  - phase-2
  - ingestion
  - api
  - fastapi
dependencies:
  - task-003
  - task-004
  - task-005
priority: high
---

## Description

Implement a FastAPI endpoint for ingesting PDF documents into the Visual RAG system.

**Scope:**
1. Implement `POST /ingest` endpoint with:
   - PDF file upload support
   - Optional doc_id override parameter
   - Background task for processing large documents
   - Error handling and logging
   - Response with ingestion summary (pages indexed, patches stored)

**Workflow:**
1. Receive PDF via file upload
2. Generate doc_id (or use provided override)
3. Convert PDF to images
4. For each page:
   a. Generate ColQwen2 embeddings
   b. Insert patches into Milvus
5. Return summary response

**API Contract:**
```
POST /ingest
Content-Type: multipart/form-data

Request:
- file: PDF file (required)
- doc_id: string (optional)

Response:
{
  "doc_id": "string",
  "pages_indexed": int,
  "patches_stored": int,
  "status": "completed" | "failed"
}
```

**Key Files to Create:**
- `src/api/routers/ingest.py`
- `src/services/ingestion_service.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 POST /ingest endpoint accepts PDF file upload
- [x] #2 Optional doc_id parameter overrides auto-generated ID
- [x] #3 Response includes pages indexed and patches stored
- [x] #4 Endpoint handles errors gracefully with proper HTTP status codes
- [x] #5 End-to-end test with ColPali paper PDF succeeds
- [x] #6 Patches verified in Milvus after ingestion
<!-- AC:END -->
