from fastapi import APIRouter

from app.api.v1 import documents, generate, ingest, search

api_router = APIRouter()

api_router.include_router(ingest.router, tags=["ingestion"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(generate.router, tags=["generation"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
