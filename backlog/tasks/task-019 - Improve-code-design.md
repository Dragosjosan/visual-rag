---
id: task-019
title: Improve code design
status: In Progress
assignee: []
created_date: '2026-01-31 14:21'
updated_date: '2026-01-31 21:28'
labels: []
dependencies: []
---

## Description

As an Software Engineer I want to use best practices in regard to software.
- The code needs to be clean, methods short and do one thing.
- The code needs to be pythonic.

**Current problems I spotted:**
- The current services are implemented through a method, which makes the service global using the `global` keyword. This is not a pattern I want to use. As example take the `get_search_service` method.
- Do we need to call the Milvus `flush` method each time when searching for a query?
- All retrieved results from Milvus have the same score. Check `Results object`.

## Implementation Notes

## Fix: Two-Stage MaxSim Retrieval for ColPali/ColQwen2

Per the official Milvus ColPali documentation, multi-vector retrieval requires a **two-stage approach**:

**Reference**: https://github.com/milvus-io/milvus-docs/blob/v2.6.x/site/en/tutorials/use_ColPali_with_milvus.md

### Stage 1: Search Phase
Search with each query vector to get candidate `doc_ids`. The current implementation does this correctly.

### Stage 2: Rerank Phase
For each candidate document, fetch ALL embeddings and compute the proper MaxSim score:

```python
def rerank_single_doc(doc_id, query_data, client, collection_name):
    doc_embeddings = client.query(
        collection_name=collection_name,
        filter=f"doc_id in [{doc_id}]",
        output_fields=["vector", "page_number"],
        limit=1000,
    )
    doc_vecs = np.vstack([doc["vector"] for doc in doc_embeddings])
    # MaxSim: for each query token, find max similarity to any doc patch, then sum
    score = np.dot(query_data, doc_vecs.T).max(axis=1).sum()
    return score
```

### MaxSim Formula
```
score = sum over query_tokens of: max over doc_patches of: similarity(query_token, doc_patch)
```

This ensures that:
1. Each query token contributes to the final score
2. The best-matching patch per query token is used
3. Pages with more relevant patches score higher

## Description
