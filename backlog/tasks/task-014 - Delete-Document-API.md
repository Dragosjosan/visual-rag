---
id: task-014
title: Delete Document API Endpoint
status: Done
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-29'
labels: [api, milvus]
dependencies: []
priority: medium
---

## Description

Add DELETE endpoint to remove document data from Milvus by document name.

**Scope:**
1. Add `DELETE /api/documents/{doc_name}` endpoint
2. Lookup doc_id from `data/documents/{doc_name}/original.pdf`
3. Delete patches from Milvus using existing `milvus_service.delete_document()`
4. Optionally delete local files (PDF and images)

**Files modified:**
- `app/api/documents.py` - Added DELETE endpoint
- `app/services/document_service.py` - Added delete_document function
- `app/models/document.py` - Added DeleteDocumentResponse model

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 DELETE /api/documents/{doc_name} removes Milvus data
- [x] #2 Returns count of deleted patches
- [x] #3 Returns 404 if document not found
<!-- AC:END -->
