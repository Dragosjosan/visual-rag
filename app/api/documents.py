from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from app.core.config import settings
from app.models.document import DeleteDocumentResponse, DocumentUploadResponse
from app.services.document_service import delete_document, handle_document_upload

router = APIRouter()

DATA_DIR = Path(settings.documents_dir)
DATA_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        doc_id, doc_name, pdf_path, page_count = await handle_document_upload(
            file=file,
            data_dir=DATA_DIR,
            dpi=settings.pdf_dpi,
        )

        return DocumentUploadResponse(
            doc_id=doc_id,
            doc_name=doc_name,
            page_count=page_count,
            pdf_path=str(pdf_path),
        )

    except ValueError as exc:
        logger.error(f"Validation error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.opt(exception=exc).error("Unexpected error during document upload")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{doc_name}", response_model=DeleteDocumentResponse)
async def delete_document_endpoint(doc_name: str):
    try:
        doc_id, patches_deleted = delete_document(doc_name, DATA_DIR)

        return DeleteDocumentResponse(
            doc_name=doc_name,
            doc_id=doc_id,
            patches_deleted=patches_deleted,
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to delete document: {doc_name}")
        raise HTTPException(status_code=500, detail="Failed to delete document") from exc
