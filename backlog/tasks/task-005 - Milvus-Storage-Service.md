---
id: task-005
title: Milvus Storage Service
status: In Progress
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-29 15:03'
labels:
  - phase-2
  - ingestion
  - database
dependencies:
  - task-002
priority: high
---

## Description

Implement the Milvus service for storing and retrieving patch embeddings with the flattened schema design.

**Scope:**
1. Implement `app/services/milvus_service.py` with:
   - `_ensure_collection()` - Create collection if not exists
   - `_create_collection()` - Define schema and indexes
   - `insert_page_embeddings()` - Insert all patches for a page (1024 rows)
   - `search_patches()` - ANN search for similar patches
   - `get_page_embeddings()` - Retrieve all patches for a specific page
   - `delete_document()` - Remove all patches for a document

**Schema:**
| Field | Type | Description |
|-------|------|-------------|
| patch_id | INT64 (PK, auto) | Auto-generated primary key |
| doc_id | VARCHAR(64) | Document identifier |
| page_number | INT32 | 1-indexed page number |
| patch_index | INT32 | Position within page (0-1023) |
| embedding | FLOAT_VECTOR(128) | Patch embedding |

**Indexes:**
- HNSW on `embedding` (metric: IP, M=16, efConstruction=256)
- Trie on `doc_id` for filtering

**Key Files to Create:**
- `app/services/milvus_service.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Collection created with correct schema
- [ ] #2 HNSW index created on embedding field
- [ ] #3 insert_page_embeddings() inserts ~1024 rows per page
- [ ] #4 search_patches() returns top-k results with scores
- [ ] #5 get_page_embeddings() retrieves all patches for a page
- [ ] #6 delete_document() removes all patches for a doc_id
<!-- AC:END -->
