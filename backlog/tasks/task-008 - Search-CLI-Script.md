---
id: task-008
title: Search CLI Script
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [phase-3, retrieval, cli]
dependencies: [task-007]
priority: high
---

## Description

Implement the standalone CLI script for searching indexed documents using MaxSim retrieval.

**Scope:**
1. Implement `scripts/search.py` with:
   - CLI argument parsing (query text, top-k)
   - Formatted output with scores
   - Optional JSON output mode
   - Timing information

**Usage:**
```bash
# Basic search
python scripts/search.py "What is the MaxSim formula?"

# With custom top-k
python scripts/search.py "ColPali performance" --top-k 10

# JSON output
python scripts/search.py "late interaction" --json
```

**Output Format:**
```
Query: What is the MaxSim formula?
Results (top 5):

1. doc_id: abc123, page: 6, score: 42.31
2. doc_id: abc123, page: 7, score: 38.92
3. doc_id: abc123, page: 2, score: 25.14
...

Search completed in 0.23s
```

**Key Files to Create:**
- `scripts/search.py`

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CLI accepts query text as argument
- [ ] #2 Results show doc_id, page_number, and score
- [ ] #3 Results are sorted by score descending
- [ ] #4 --top-k parameter controls result count
- [ ] #5 --json flag outputs JSON format
- [ ] #6 Timing information displayed
<!-- AC:END -->
