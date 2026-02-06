---
id: task-021
title: Add Azure AI Search
status: In Progress
assignee: []
created_date: '2026-02-01 17:25'
updated_date: '2026-02-01'
labels: [feature, azure, vector-db]
dependencies: []
priority: high
---

## Description

Add Azure AI Search as a parallel vector database with its own set of API endpoints (`/api/v1/azure/*`) running alongside existing Milvus endpoints (`/api/v1/*`). Both systems operate independently.

## API Structure

| Feature | Milvus (existing) | Azure AI Search (new) |
|---------|-------------------|----------------------|
| Ingest PDF | POST /api/v1/ingest | POST /api/v1/azure/ingest |
| Search | POST /api/v1/search | POST /api/v1/azure/search |
| Delete Doc | DELETE /api/v1/documents/{name} | DELETE /api/v1/azure/documents/{name} |
| List Docs | GET /api/v1/documents | GET /api/v1/azure/documents |
| Generate | POST /api/v1/generate | POST /api/v1/azure/generate |

## Files to Create

### Services

1. **`src/services/azure_search_service.py`** - Azure AI Search service (mirrors MilvusService interface):
   - `insert_page_embeddings(doc_id, page_number, embeddings) -> int`
   - `search_pages(query_embeddings, top_k, doc_id_filter) -> list[dict]`
   - `document_exists(doc_id) -> bool`
   - `delete_document(doc_id) -> int`
   - `get_collection_stats() -> dict`
   - `drop_collection() -> None`
   - `disconnect() -> None`

2. **`src/services/azure_retrieval_service.py`** - Retrieval service using AzureSearchService

3. **`src/services/azure_ingestion_service.py`** - Ingestion service using AzureSearchService

4. **`src/services/azure_search_query_service.py`** - Search service orchestrating Azure retrieval

### API Routers

5. **`src/api/v1/azure/__init__.py`** - Package init

6. **`src/api/v1/azure/ingest.py`** - Router for PDF ingestion to Azure AI Search

7. **`src/api/v1/azure/search.py`** - Router for search queries against Azure AI Search

8. **`src/api/v1/azure/documents.py`** - Router for document management (list, delete)

9. **`src/api/v1/azure/generate.py`** - Router for RAG generation using Azure retrieval

### Tests

10. **`tests/services/test_azure_search_service.py`** - Integration tests for AzureSearchService

## Files to Modify

### 1. `src/core/config.py`
Add Azure AI Search settings:
```python
azure_search_endpoint: str = Field(default="")
azure_search_api_key: str = Field(default="")
azure_search_index_name: str = Field(default="visual_rag_patches")
```

### 2. `src/main.py`
Include Azure routers:
```python
from src.api.v1.azure import ingest, search, documents, generate

app.include_router(ingest.router, prefix="/api/v1/azure", tags=["azure-ingest"])
app.include_router(search.router, prefix="/api/v1/azure", tags=["azure-search"])
app.include_router(documents.router, prefix="/api/v1/azure", tags=["azure-documents"])
app.include_router(generate.router, prefix="/api/v1/azure", tags=["azure-generate"])
```

### 3. `pyproject.toml`
Add dependency: `azure-search-documents>=11.4.0`

## Azure Search Implementation Details

### Index Schema

| Field | Type | Properties |
|-------|------|-----------|
| patch_id | String | key=True (format: `{doc_id}_{page}_{patch}`) |
| doc_id | String | filterable=True |
| page_number | Int32 | filterable=True |
| patch_index | Int32 | - |
| embedding | Collection(Single) | dim=128, HNSW with dotProduct |

### Key Implementation Points

- Use `VectorizedQuery` for pre-computed ColPali embeddings
- Use `dotProduct` metric (equivalent to Milvus Inner Product)
- MaxSim scoring: per-token search, aggregate max scores per page
- Deletion: query by filter -> collect IDs -> batch delete (max 1000/batch)
- Lazy client initialization (singleton pattern)

## Implementation Sequence

| Step | Task |
|------|------|
| 1 | Add `azure-search-documents` to pyproject.toml |
| 2 | Add Azure config settings to config.py |
| 3 | Create `azure_search_service.py` |
| 4 | Create `azure_retrieval_service.py` |
| 5 | Create `azure_ingestion_service.py` |
| 6 | Create `azure_search_query_service.py` |
| 7 | Create `src/api/v1/azure/__init__.py` |
| 8 | Create `src/api/v1/azure/ingest.py` |
| 9 | Create `src/api/v1/azure/search.py` |
| 10 | Create `src/api/v1/azure/documents.py` |
| 11 | Create `src/api/v1/azure/generate.py` |
| 12 | Update `main.py` to include Azure routers |
| 13 | Create tests for Azure services |

## Critical Files Reference

- `src/services/milvus_service.py` - Pattern to mirror for Azure service
- `src/services/retrieval_service.py` - Pattern for Azure retrieval service
- `src/services/ingestion_service.py` - Pattern for Azure ingestion service
- `src/api/v1/ingest.py` - Pattern for Azure ingest router
- `src/api/v1/search.py` - Pattern for Azure search router

## Verification Plan

1. **Install Dependencies**
   ```bash
   uv add azure-search-documents
   ```

2. **Unit Tests**
   ```bash
   uv run pytest tests/services/test_azure_search_service.py -v
   ```

3. **End-to-End Test**
   - Set Azure credentials in .env:
     ```
     AZURE_SEARCH_ENDPOINT=https://xxx.search.windows.net
     AZURE_SEARCH_API_KEY=xxx
     ```
   - Start API: `uv run uvicorn src.main:app --reload`
   - Ingest: `POST /api/v1/azure/ingest`
   - Search: `POST /api/v1/azure/search`
   - Delete: `DELETE /api/v1/azure/documents/{name}`

4. **Verify Milvus Still Works**
   ```bash
   uv run pytest tests/services/test_milvus_service.py -v
   ```

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Azure Search service implements same interface as MilvusService
- [ ] #2 All Azure API endpoints functional (/api/v1/azure/*)
- [ ] #3 MaxSim scoring works correctly with Azure Search
- [ ] #4 Existing Milvus endpoints unaffected
- [ ] #5 Integration tests pass
<!-- AC:END -->
