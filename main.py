from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents, ingest
from app.core.config import settings

app = FastAPI(
    title="Visual RAG API",
    description="Visual RAG with ColPali and Milvus",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(ingest.router, prefix="/api", tags=["ingestion"])


@app.get("/")
def root():
    return {"message": "Visual RAG API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
