---
id: task-007
title: MaxSim Retrieval Service
status: Done
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-29 21:11'
labels:
  - phase-3
  - retrieval
dependencies:
  - task-004
  - task-005
priority: high
---

## Description

Implement retrieval service using Milvus 2.6.4+ native MAX_SIM with Array of Structs.

**MaxSim Algorithm:**
```
LI(q,d) = Σ_i max_j ⟨E_q^(i) | E_d^(j)⟩
```
For each query token, find max dot product with any document patch, then sum across all query tokens.

**Example:**
Imagine searching for "red sports car" on a page with image patches of a Ferrari.

Query tokens: ["red", "sports", "car"] → 3 embeddings
Document patches: [wheel, hood, logo, windshield, ...] → 1000 embeddings

For each query token, find the best matching patch:
- "red" → best match: hood (score: 0.85)
- "sports" → best match: logo (score: 0.72)
- "car" → best match: windshield (score: 0.91)

MaxSim score = 0.85 + 0.72 + 0.91 = 2.48

This ensures every query term contributes to the score, and unmatched patches don't hurt.

**Approach: Native MAX_SIM (Milvus 2.6.4+)**
Instead of custom two-stage retrieval, leverage Milvus native `MAX_SIM_IP` metric type with Array of Structs. Milvus implements the exact same MaxSim formula internally.

**Benefits:**
- No custom MaxSim scoring code needed
- Single query returns page-level results with MaxSim scores
- Simpler implementation, database handles the computation

**Scope:**
1. Upgrade `pymilvus` to 2.6.4+
2. Refactor `app/services/milvus_service.py`:
   - Use Array of Structs schema (all patches per page in one row)
   - Use `MAX_SIM_IP` metric type for indexing
   - Search returns page-level results directly

3. Implement `app/services/retrieval_service.py` with:
   - `retrieve()` - Query encoding + Milvus search
   - Configurable top_k_pages
   - Return ranked pages with doc_id, page_number, score

**Schema Change:**
```python
# Before: Each patch as separate row
FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)

# After: Array of Structs with all patches per page
FieldSchema(
    name="patches",
    dtype=DataType.ARRAY,
    element_type=DataType.STRUCT,
    max_capacity=1030,  # Max patches per page
    # Each struct contains a vector field
)
```

**Index with MAX_SIM:**
```python
index_params.add_index(
    field_name="patches[embedding]",
    index_type="HNSW",
    metric_type="MAX_SIM_IP",  # Native MaxSim scoring
)
```

**Key Files to Modify/Create:**
- `app/services/milvus_service.py` - Refactor to Array of Structs schema
- `app/services/retrieval_service.py` - New retrieval service

**Reference:**
- [Milvus Array of Structs Docs](https://milvus.io/docs/array-of-structs.md)
- [Milvus MAX_SIM Blog](https://milvus.io/blog/unlocking-true-entity-level-retrieval-new-array-of-structs-and-max-sim-capabilities-in-milvus.md)

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pymilvus upgraded to 2.6.4+
- [ ] #2 MilvusService uses Array of Structs schema with MAX_SIM_IP
- [ ] #3 retrieve() returns ranked page results with doc_id, page_number, score
- [ ] #4 Query "MaxSim formula" retrieves pages 6-7 of ColPali paper
- [ ] #5 Retrieval latency <500ms for 1000 pages corpus
<!-- AC:END -->
