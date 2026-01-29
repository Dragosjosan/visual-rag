---
id: task-007
title: MaxSim Retrieval Service
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-3, retrieval]
dependencies: [task-004, task-005]
priority: high
---

## Description

Implement the two-stage retrieval service with MaxSim scoring for late interaction.

**Scope:**
1. Implement `app/utils/scoring.py` with:
   - `compute_maxsim()` - Compute Late Interaction MaxSim score
   - Optimized numpy implementation

2. Implement `app/services/retrieval_service.py` with:
   - `retrieve()` - Full two-stage retrieval pipeline
   - Configurable top_k_patches and top_k_pages

**MaxSim Algorithm:**
```
LI(q,d) = Σ_i max_j ⟨E_q^(i) | E_d^(j)⟩
```
For each query token, find max dot product with any doc patch, then sum across all query tokens.

**Two-Stage Retrieval:**
1. Encode query → multi-vector [N_tokens, 128]
2. ANN search per query token → candidate patches (top 100 each)
3. Collect unique (doc_id, page_number) pairs as candidates
4. Fetch full page embeddings for each candidate
5. Compute full MaxSim score for each candidate page
6. Return top-k pages sorted by score

**Key Files to Create:**
- `app/utils/scoring.py`
- `app/services/retrieval_service.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 compute_maxsim() correctly implements the formula
- [ ] #2 Two-stage retrieval returns ranked page results
- [ ] #3 Results include doc_id, page_number, and score
- [ ] #4 Query "MaxSim formula" retrieves pages 6-7 of ColPali paper
- [ ] #5 Retrieval latency <500ms for 1000 pages corpus
<!-- AC:END -->
