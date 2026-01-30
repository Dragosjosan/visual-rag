import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.config import settings
from app.models.document import GenerateRequest, GenerateResponse, SourceReference
from app.services.generation_service import get_generation_service
from app.services.search_service import get_search_service
from app.utils.document_utils import get_doc_id_to_name_mapping, get_page_image_path

router = APIRouter()

DATA_DIR = Path(settings.documents_dir)


@router.post("/generate", response_model=GenerateResponse)
async def generate_answer(request: GenerateRequest) -> GenerateResponse:
    try:
        start_time = time.perf_counter()

        search_service = get_search_service()
        search_response = search_service.search(
            query=request.query,
            top_k=request.top_k,
            doc_id_filter=request.doc_id,
        )

        if not search_response.results:
            raise ValueError("No relevant documents found for the query")

        doc_id_to_name = get_doc_id_to_name_mapping(DATA_DIR)

        image_paths = []
        sources = []
        for result in search_response.results:
            doc_name = doc_id_to_name.get(result.doc_id)
            if not doc_name:
                logger.warning(f"Could not find doc_name for doc_id: {result.doc_id}")
                continue

            image_path = get_page_image_path(DATA_DIR, doc_name, result.page_number)
            if not image_path.exists():
                logger.warning(f"Image not found: {image_path}")
                continue

            image_paths.append(image_path)
            sources.append(
                SourceReference(
                    doc_id=result.doc_id,
                    page_number=result.page_number,
                    score=result.score,
                )
            )

        if not image_paths:
            raise ValueError("Could not load any document images")

        generation_service = get_generation_service()
        answer = await generation_service.generate_answer(
            query=request.query,
            images=image_paths,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Generation completed: query='{request.query[:50]}...', sources={len(sources)}, time={elapsed_ms:.2f}ms"
        )

        return GenerateResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            generation_time_ms=round(elapsed_ms, 2),
        )

    except ValueError as e:
        logger.warning(f"Invalid generate request: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail="Generation failed") from None
