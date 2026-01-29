---
id: task-010
title: Generation CLI Script
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-4, generation, cli]
dependencies: [task-007, task-009]
priority: medium
---

## Description

Implement the standalone CLI script for end-to-end RAG: retrieve relevant pages and generate answers using the VLM.

**Scope:**
1. Implement `scripts/generation.py` with:
   - CLI argument parsing (query, top-k pages, optional PDF path for images)
   - Integration with retrieval service
   - Integration with generation service
   - Progress indicators
   - Formatted output

**Workflow:**
1. Encode query and retrieve top-k pages
2. Load page images (from cached images or re-convert PDF)
3. Pass images + query to VLM
4. Display generated answer

**Usage:**
```bash
# Basic RAG query
python scripts/generation.py "What is ColPali's performance on DocVQA?"

# With more context pages
python scripts/generation.py "Explain the MaxSim formula" --top-k 3

# Specify PDF for image source
python scripts/generation.py "What is the benchmark?" --pdf data/pdfs/paper.pdf
```

**Output Format:**
```
Query: What is ColPali's performance on DocVQA?

Retrieving relevant pages...
Found 3 relevant pages (0.24s)
  - doc_id: abc123, page: 7, score: 45.2
  - doc_id: abc123, page: 2, score: 32.1
  - doc_id: abc123, page: 8, score: 28.9

Generating answer...

Answer:
According to Table 2 in the document, ColPali achieves 54.4 nDCG@5 on DocVQA,
which significantly outperforms the baseline methods...

Total time: 8.3s
```

**Key Files to Create:**
- `scripts/generation.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CLI performs retrieval + generation pipeline
- [ ] #2 Retrieved pages displayed with scores
- [ ] #3 Generated answer is relevant to query
- [ ] #4 Progress indicators show each step
- [ ] #5 Total time displayed at end
- [ ] #6 End-to-end test produces accurate answer
<!-- AC:END -->
