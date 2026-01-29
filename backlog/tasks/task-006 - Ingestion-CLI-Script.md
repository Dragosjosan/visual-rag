---
id: task-006
title: Ingestion CLI Script
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-2, ingestion, cli]
dependencies: [task-003, task-004, task-005]
priority: high
---

## Description

Implement the standalone CLI script for ingesting PDF documents into the Visual RAG system.

**Scope:**
1. Implement `scripts/ingest.py` with:
   - CLI argument parsing (PDF path, optional doc_id override)
   - Progress bar for multi-page documents
   - Batch processing for multiple PDFs
   - Error handling and logging
   - Summary output (pages indexed, patches stored, time taken)

**Workflow:**
1. Load PDF and generate doc_id
2. Convert PDF to images
3. For each page:
   a. Generate ColQwen2 embeddings
   b. Insert patches into Milvus
4. Report summary

**Usage:**
```bash
# Single PDF
python scripts/ingest.py data/pdfs/document.pdf

# Multiple PDFs
python scripts/ingest.py data/pdfs/

# With custom doc_id
python scripts/ingest.py data/pdfs/document.pdf --doc-id my-doc-001
```

**Key Files to Create:**
- `scripts/ingest.py`
- `data/pdfs/` directory

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CLI accepts PDF file path as argument
- [ ] #2 Progress bar shows indexing progress
- [ ] #3 Summary shows pages indexed and patches stored
- [ ] #4 Batch mode processes all PDFs in a directory
- [ ] #5 End-to-end test with ColPali paper PDF succeeds
- [ ] #6 Patches verified in Milvus after ingestion
<!-- AC:END -->
