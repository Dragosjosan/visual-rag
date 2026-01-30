from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger

from src.core.config import settings
from src.models.document import IngestionResponse
from src.services.ingestion_service import ingest_uploaded_pdf

router = APIRouter()

TEMP_DIR = Path(settings.documents_dir) / "temp"


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(
    file: UploadFile = File(...),  # noqa: B008
    doc_id: str | None = Form(default=None),
):
    try:
        result_doc_id, pages_indexed, patches_stored = await ingest_uploaded_pdf(
            file=file,
            temp_dir=TEMP_DIR,
            doc_id=doc_id,
            dpi=settings.pdf_dpi,
        )

        return IngestionResponse(
            doc_id=result_doc_id,
            pages_indexed=pages_indexed,
            patches_stored=patches_stored,
            status="completed",
        )

    except ValueError as e:
        logger.error(f"Validation error during ingestion: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except FileNotFoundError as e:
        logger.error(f"File not found during ingestion: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.opt(exception=e).error("Ingestion failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
