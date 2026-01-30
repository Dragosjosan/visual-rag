from fastapi import APIRouter, HTTPException
from loguru import logger

from src.models.document import SearchRequest, SearchResponse
from src.services.search_service import get_search_service

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest) -> SearchResponse:
    try:
        search_service = get_search_service()
        return search_service.search(
            query=request.query,
            top_k=request.top_k,
            doc_id_filter=request.doc_id,
        )
    except ValueError as e:
        logger.warning(f"Invalid search request: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed") from None
