---
id: task-015
title: Add Attu to Docker Compose
status: Completed
assignee: []
created_date: '2026-01-29'
updated_date: '2026-01-30'
labels:
  - infrastructure
  - milvus
dependencies: []
priority: low
---

## Description

Add Attu (Milvus GUI) to docker-compose for easier data inspection.

**Scope:**
1. Add Attu service to `docker-compose.yml`
2. Configure connection to Milvus
3. Expose on port 8080

**Configuration:**
```yaml
attu:
  image: zilliz/attu:latest
  ports:
    - "8080:3000"
  environment:
    - MILVUS_URL=milvus:19530
  depends_on:
    - milvus
```

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Attu accessible at http://localhost:8080
- [x] #2 Can browse collections and data
<!-- AC:END -->
