---
id: task-020
title: MaxSim Scoring Bug Fix
status: Done
assignee: []
created_date: '2026-02-01 13:30'
updated_date: '2026-02-01 13:30'
labels: [bug-fix, milvus, search]
dependencies: []
---

## Problem

Search results returned identical similarity scores (0.9257) for all pages.

## Root Cause

ColQwen2 produces multi-vector embeddings where:
- Token 0 is a fixed CLS/prompt embedding (identical for all images)
- Tokens 5+ are actual image patch embeddings (vary per image)

The old aggregation code kept only the MAX score across all query tokens:
```python
if score > page_scores.get(key, float("-inf")):
    page_scores[key] = score
```

**What happened:**
1. Query token 0 (fixed) matched patch 0 (also fixed) on ALL pages with score 0.925
2. This was the highest score, so ALL pages got 0.925
3. Scores from other tokens that matched actual image content were discarded

## Solution

Implemented proper MaxSim scoring in `src/services/milvus_service.py`:

```python
# For each query token, track its max score per page
token_page_max: dict[tuple[str, int], float] = {}
for hits in results:
    for hit in hits:
        if score > token_page_max.get(key, float("-inf")):
            token_page_max[key] = score

# SUM across all tokens (not just keep max)
for key, score in token_page_max.items():
    page_scores[key] = page_scores.get(key, 0.0) + score
```

Now each token contributes to the final score, so pages with better content matches score higher.

## Additional Fix: Test Isolation

Tests destroyed production data by using the same collection name. Fixed with:
```python
TEST_COLLECTION_NAME = "visual_rag_patches_test"

@pytest.fixture
def milvus_service(monkeypatch):
    monkeypatch.setattr(settings, "milvus_collection_name", TEST_COLLECTION_NAME)
```

## Testing

```bash
# Verify embeddings vary across pages (patches 5+ should differ)
uv run python backlog/scripts/check_embeddings.py

# Verify search returns varied scores
uv run python backlog/scripts/test_search_scores.py
```

## References

- MaxSim formula: `score = sum over query_tokens of: max over page_patches of: similarity(query_token, patch)`
- Milvus ColPali Tutorial: https://github.com/milvus-io/milvus-docs/blob/v2.6.x/site/en/tutorials/use_ColPali_with_milvus.md
