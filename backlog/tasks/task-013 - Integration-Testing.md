---
id: task-013
title: Integration Testing
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-5, testing]
dependencies: [task-012]
priority: medium
---

## Description

Implement integration tests to verify the complete Visual RAG pipeline works end-to-end.

**Scope:**
1. Create test fixtures:
   - Sample PDF document
   - Expected query results
   - Test configuration

2. Implement tests in `tests/`:
   - `test_pdf_processor.py` - PDF to image conversion
   - `test_embedding_service.py` - ColQwen2 embeddings
   - `test_milvus_service.py` - Storage operations
   - `test_retrieval_service.py` - MaxSim retrieval
   - `test_integration.py` - Full pipeline tests

3. Test scenarios:
   - Ingest ColPali paper PDF
   - Search for "MaxSim formula" → verify pages 6-7 in top results
   - Search for "ViDoRe benchmark" → verify page 4 in top results
   - Generate answer for "What is ColPali's DocVQA performance?"
   - Verify answer mentions ~54.4 nDCG@5

**Key Files to Create:**
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_pdf_processor.py`
- `tests/test_embedding_service.py`
- `tests/test_milvus_service.py`
- `tests/test_retrieval_service.py`
- `tests/test_integration.py`

**Test Commands:**
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app

# Run specific test
pytest tests/test_integration.py -v
```

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All unit tests pass
- [ ] #2 Integration test ingests PDF successfully
- [ ] #3 Integration test retrieves correct pages
- [ ] #4 Integration test generates relevant answer
- [ ] #5 Test coverage > 70%
- [ ] #6 Tests run in CI-friendly mode (no GPU required for mocks)
<!-- AC:END -->
