---
id: task-015
title: Add Attu to Docker Compose
status: To Do
assignee: []
created_date: '2026-01-29'
labels: [infrastructure, milvus]
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
- [ ] #1 Attu accessible at http://localhost:8080
- [ ] #2 Can browse collections and data
<!-- AC:END -->
