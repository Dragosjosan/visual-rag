---
id: task-004
title: ColQwen2 Embedding Service
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-2, ingestion, ml]
dependencies: [task-002]
priority: high
---

## Description

Implement the embedding service using ColQwen2 (via HuggingFace transformers) to generate multi-vector embeddings from document page images.

**Scope:**
1. Implement `app/services/embedding_service.py` with:
   - Model loading with MPS (Metal) support for M4
   - `encode_images()` - Encode list of images to multi-vector embeddings
   - `encode_query()` - Encode query text to multi-vector embedding
2. Implement `app/core/model_loader.py`:
   - Singleton pattern for model loading
   - Lazy loading to reduce startup time

**Technical Details:**
- Model: `vidore/colqwen2-v1.0-hf`
- Device: MPS (Metal Performance Shaders) for M4
- Dtype: bfloat16 for memory efficiency
- Output per image: ~1024 patches x 128 dimensions
- Output per query: N_tokens x 128 dimensions

**Key Files to Create:**
- `app/services/embedding_service.py`
- `app/core/model_loader.py`

**Model Download:**
First run will automatically download the model (~5GB) from HuggingFace.

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Model loads successfully on MPS device
- [ ] #2 encode_images() returns tensors of shape [N_patches, 128]
- [ ] #3 encode_query() returns tensor of shape [N_tokens, 128]
- [ ] #4 Embedding generation works with bfloat16
- [ ] #5 Single image encoding completes in <1 second on M4
<!-- AC:END -->
