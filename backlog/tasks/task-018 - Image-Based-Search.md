---
id: task-018
title: Image-Based Search Endpoint
status: Todo
assignee: []
created_date: '2026-01-31'
updated_date: '2026-01-31'
labels: [api, search, multimodal]
dependencies: []
priority: medium
---

## Description

Add an endpoint to search documents using an image query instead of text.

**Context:**
- ColQwen2 is a vision-language model that supports both text and image queries
- `EmbeddingService.encode_images()` already exists and is used during document ingestion
- The same method can be used to encode an image query for search
- This enables visual similarity search (e.g., find pages containing similar diagrams, charts, or layouts)

**Scope:**
1. Add `POST /api/v1/search/image` - Search using an uploaded image
2. Accept image file upload (JPEG, PNG, etc.)
3. Encode query image using `EmbeddingService.encode_images()`
4. Search Milvus with image embeddings (same flow as text search)
5. Return matching document pages ranked by similarity

**Request:**
- Multipart form with image file
- `top_k` parameter (default: 5)
- Optional `doc_id` filter

**Response:**
- Same as text search: `SearchResponse` with results, total count, search time

**Files to modify:**
- `src/api/v1/search.py` - Add image search endpoint
- `src/services/search_service.py` - Add image search method
- `src/services/retrieval_service.py` - Add image query retrieval method

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 POST /api/v1/search/image accepts image file upload
- [ ] #2 Supports common image formats (JPEG, PNG, WebP)
- [ ] #3 Uses ColQwen2 to encode the query image
- [ ] #4 Returns ranked document pages by visual similarity
- [ ] #5 Supports top_k and doc_id filter parameters
- [ ] #6 Returns 400 for invalid image files
- [ ] #7 Response format matches text search endpoint
<!-- AC:END -->
