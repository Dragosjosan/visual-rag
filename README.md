# Visual RAG

Visual RAG with ColPali and Milvus.

## API Endpoints

### Upload Document
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.pdf"
```

### Ingest Document
```bash
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@document.pdf"
```

### Search
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ViDoRe", "top_k": 5}'
```

### Delete Document
```bash
curl -X DELETE http://localhost:8000/api/documents/{doc_name}
```

## View Data in Milvus UI (Attu)

```bash
docker run -p 8080:3000 -e MILVUS_URL=host.docker.internal:19530 zilliz/attu:latest
```

Open http://localhost:8080 in your browser.
