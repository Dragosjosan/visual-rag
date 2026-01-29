---
id: task-008
title: Search API Endpoint
status: Done
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-29'
labels:
  - phase-3
  - retrieval
  - api
dependencies:
  - task-007
priority: high
---

## Description

Implement the search API endpoint for querying indexed documents using MaxSim retrieval.

**Scope:**
1. Implement `app/api/search.py` router with POST /api/search endpoint
2. Implement `app/services/search_service.py` with search logic
3. Add request/response models to `app/models/document.py`
4. Register router in `main.py`

**Usage:**
```bash
# Basic search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the MaxSim formula?"}'

# With custom top-k
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ColPali performance", "top_k": 10}'

# Filter by document
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "late interaction", "doc_id": "abc123"}'
```

**Response Format:**
```json
{
  "query": "What is the MaxSim formula?",
  "results": [
    {"doc_id": "abc123", "page_number": 6, "score": 42.31},
    {"doc_id": "abc123", "page_number": 7, "score": 38.92},
    {"doc_id": "abc123", "page_number": 2, "score": 25.14}
  ],
  "total_results": 3,
  "search_time_ms": 230.45
}
```

**Files Created:**
- `app/api/search.py`
- `app/services/search_service.py`

**Files Modified:**
- `app/models/document.py`
- `main.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 POST /api/search endpoint accepts query in request body
- [x] #2 Results show doc_id, page_number, and score
- [x] #3 Results are sorted by score descending
- [x] #4 top_k parameter controls result count (default: 5)
- [x] #5 Optional doc_id filter for document-specific search
- [x] #6 Timing information in response (search_time_ms)
<!-- AC:END -->
