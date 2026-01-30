---
id: task-009
title: VLM Generation Service
status: Done
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-30 09:31'
labels:
  - phase-4
  - generation
  - vlm
dependencies:
  - task-002
priority: medium
---

## Description

Implement the VLM generation service using Ollama with Qwen2-VL for answer generation based on retrieved document images.

**Scope:**
1. Set up Ollama on host machine:
   - Install: `brew install ollama`
   - Pull model: `ollama pull qwen3-vl:8b`
   - Verify Metal acceleration

2. Implement `app/services/generation_service.py` with:
   - `generate_answer()` - Generate answer from query + images
   - Async HTTP client for Ollama API
   - Image to base64 conversion
   - Configurable timeout and model

**Technical Details:**
- Ollama API endpoint: `http://localhost:11434/api/generate`
- Model: `qwen3-vl:8b`
- Input: Query text + base64 encoded images
- Output: Generated answer text
- Timeout: 120 seconds (VLM can be slow)

**Prompt Template:**
```
You are a helpful assistant that answers questions based on the provided document images.

Question: {query}

Please analyze the document images and provide a clear, accurate answer based solely on the information visible in the images. If the answer cannot be found in the images, say so.
```

**Key Files to Create:**
- `app/services/generation_service.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Ollama installed and running on host
- [ ] #2 qwen2-vl:7b model pulled and working
- [ ] #3 Metal acceleration verified in Ollama logs
- [ ] #4 generate_answer() returns coherent responses
- [ ] #5 Multiple images can be passed to the model
- [ ] #6 Generation completes within 60 seconds
<!-- AC:END -->
