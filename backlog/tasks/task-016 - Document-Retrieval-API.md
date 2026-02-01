---
id: task-016
title: Document Retrieval API Endpoints
status: Todo
assignee: []
created_date: '2026-01-30'
updated_date: '2026-01-30'
labels: [api, documents]
dependencies: []
priority: medium
---

## Description

Add GET endpoints to retrieve document information by doc_id or doc_name, and list all documents.

**Context:**
- `doc_id` is a SHA256 hash of the PDF content (64-char hex string)
- `doc_name` is the filename stem used for directory organization
- Currently no way to list documents or retrieve metadata after upload

**Scope:**
1. Add `GET /api/v1/documents/` - List all documents
2. Add `GET /api/v1/documents/{doc_id}` - Get document by doc_id
3. Add `GET /api/v1/documents/name/{doc_name}` - Get document by name

**Response models:**
- `DocumentInfo` - Single document metadata (doc_id, doc_name, page_count, pdf_path)
- `DocumentListResponse` - List of DocumentInfo objects

**Files to modify:**
- `src/api/v1/documents.py` - Add GET endpoints
- `src/services/document_service.py` - Add list and get functions
- `src/models/document.py` - Add response models if needed

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 GET /api/v1/documents/ returns list of all documents
- [ ] #2 GET /api/v1/documents/{doc_id} returns document by SHA256 hash
- [ ] #3 GET /api/v1/documents/name/{doc_name} returns document by name
- [ ] #4 Returns 404 if document not found
- [ ] #5 Each response includes doc_id, doc_name, page_count, pdf_path
<!-- AC:END -->
