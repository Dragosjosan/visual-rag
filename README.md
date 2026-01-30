# Visual RAG

Visual RAG system using ColPali for visual embeddings and Milvus for vector storage.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Make (optional, for convenience commands)

### Starting the Application

```bash
# Build and start all services (Milvus, etcd, minio, Attu)
make build
make run
```

Services will be available at:
- **Swagger API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000
- **Attu (Milvus UI)**: http://localhost:8080
- **Milvus**: localhost:19530

### Stopping the Application

```bash
make down
```

## API Documentation

FastAPI provides interactive API documentation via Swagger UI. Access it at:

**http://localhost:8000/docs**

The Swagger UI allows you to:
- View all available endpoints and their parameters
- Try out API calls directly in your browser
- See request/response schemas and examples
- Download the OpenAPI specification

Alternative documentation format available at: http://localhost:8000/redoc

## Complete Workflow

### 1. Ingest a Document

The `/api/v1/ingest` endpoint processes and stores a PDF document.

**Using Swagger UI:**
1. Navigate to http://localhost:8000/docs
2. Find the `POST /api/v1/ingest` endpoint
3. Click "Try it out"
4. Upload your PDF file
5. Click "Execute"

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@document.pdf"
```

**What happens during ingestion:**
1. PDF is converted to images (one per page)
2. Visual embeddings are generated using ColPali model
3. Embeddings are stored in Milvus vector database
4. Each page becomes a searchable chunk

**Expected successful response:**
```json
{
  "status": "success",
  "document_name": "document.pdf",
  "pages_processed": 10,
  "collection": "visual_rag"
}
```

**If document already exists:**
- The system will return an error indicating the document is already ingested
- To re-ingest, first delete the document using the delete endpoint
- Duplicate prevention avoids redundant processing and storage

### 2. Search for Information

Search using natural language queries.

**Using Swagger UI:**
1. Navigate to http://localhost:8000/docs
2. Find the `POST /api/v1/search` endpoint
3. Click "Try it out"
4. Enter your search query and top_k value
5. Click "Execute"

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ViDoRe?", "top_k": 5}'
```

**Parameters:**
- `query`: Natural language question or search term
- `top_k`: Number of results to return (default: 5)

**Expected successful response:**
```json
{
  "results": [
    {
      "document": "document.pdf",
      "page": 3,
      "score": 0.89,
      "image": "base64_encoded_page_image"
    }
  ],
  "query": "What is ViDoRe?",
  "total_results": 5
}
```

**What happens during search:**
1. Query is encoded using ColPali model
2. Similarity search performed in Milvus
3. Top-k most relevant pages are retrieved
4. Results include page images and relevance scores

### 3. Delete a Document

Remove a document and all its pages from the system.

**Using Swagger UI:**
1. Navigate to http://localhost:8000/docs
2. Find the `DELETE /api/v1/documents/{document_name}` endpoint
3. Click "Try it out"
4. Enter the document name
5. Click "Execute"

**Using curl:**
```bash
curl -X DELETE http://localhost:8000/api/v1/documents/document.pdf
```

**Expected successful response:**
```json
{
  "status": "success",
  "message": "Document deleted",
  "pages_deleted": 10
}
```

## View Data in Milvus UI (Attu)

Attu is included in the docker-compose setup and starts automatically.

Access it at: http://localhost:8080

**What you can do in Attu:**
- Browse all collections and documents
- View collection schemas and statistics
- Inspect individual vectors and metadata
- Monitor Milvus performance
- Debug search results

**Connection details (pre-configured):**
- Host: milvus
- Port: 19530

## Troubleshooting

### Services won't start
```bash
# Check service logs
docker compose -f docker-compose.yml logs -f

# Restart services
make down
make run
```

### Milvus connection issues
- Ensure all services are healthy: `docker compose -f docker-compose.yml ps`
- Milvus requires etcd and minio to be running first
- Wait 30-60 seconds after startup for Milvus to be fully ready

### API endpoint not found (404 errors)
- Verify you're using the correct API version prefix: `/api/v1/`
- Check the Swagger docs at http://localhost:8000/docs for the current endpoint paths

### Clear all data
```bash
# Stop services and remove all volumes
docker compose -f docker-compose.yml down -v
```
