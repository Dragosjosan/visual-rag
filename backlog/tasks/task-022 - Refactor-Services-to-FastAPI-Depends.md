---
id: task-022
title: Refactor Services to Use FastAPI Depends Pattern
status: Open
assignee: []
created_date: '2026-02-01 21:45'
labels: [refactoring, code-quality]
dependencies: []
priority: low
---

## Description

As a Software Engineer I want to refactor the service layer to use FastAPI's `Depends()` pattern instead of the current `global` keyword pattern for singleton services.

## Current State

Services currently use a module-level variable with `global` keyword:

```python
_search_service: SearchService | None = None

def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
```

## Target State

Use FastAPI's dependency injection system:

```python
from functools import lru_cache

@lru_cache
def get_retrieval_service() -> RetrievalService:
    return RetrievalService()

def get_search_service(
    retrieval: RetrievalService = Depends(get_retrieval_service)
) -> SearchService:
    return SearchService(retrieval)
```

## Benefits

- Explicit dependency graph
- Easier testing with dependency overrides
- Follows FastAPI conventions
- Removes `global` keyword usage

## Files to Refactor

- `src/services/search_service.py`
- `src/services/retrieval_service.py`
- `src/services/milvus_service.py`
- `src/services/generation_service.py`
- Update all API routers that use these services

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Replace `global` pattern with `@lru_cache` in all services
- [ ] #2 Update API routers to use `Depends()` for service injection
- [ ] #3 Update tests to use FastAPI's dependency override mechanism
- [ ] #4 All existing tests pass
<!-- AC:END -->
