from pathlib import Path

from fastapi import UploadFile
from loguru import logger
from PIL import Image

from src.models.document import validate_filename
from src.services.embedding_service import EmbeddingService, get_embedding_service
from src.services.milvus_service import MilvusService, get_milvus_service
from src.services.pdf_processor import convert_pdf_to_images, generate_doc_id


class IngestionService:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        milvus_service: MilvusService | None = None,
    ) -> None:
        self._embedding_service = embedding_service
        self._milvus_service = milvus_service

    @property
    def embedding_service(self) -> EmbeddingService:
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    @property
    def milvus_service(self) -> MilvusService:
        if self._milvus_service is None:
            self._milvus_service = get_milvus_service()
        return self._milvus_service

    def ingest_pdf_from_path(
        self,
        pdf_path: Path,
        doc_id: str | None = None,
        dpi: int = 144,
        max_pages: int | None = None,
    ) -> tuple[str, int, int]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if doc_id is None:
            doc_id = generate_doc_id(pdf_path)

        logger.info(f"Starting ingestion for doc_id={doc_id}, path={pdf_path}")

        images = convert_pdf_to_images(pdf_path, dpi=dpi)

        if max_pages is not None and max_pages > 0:
            images = images[:max_pages]

        pages_indexed = len(images)

        total_patches = self._process_and_store_pages_atomic(doc_id, images)

        logger.success(f"Ingestion complete: doc_id={doc_id}, pages={pages_indexed}, patches={total_patches}")

        return doc_id, pages_indexed, total_patches

    def _process_and_store_pages_atomic(
        self,
        doc_id: str,
        images: list[tuple[int, Image.Image]],
    ) -> int:
        total_patches = 0

        try:
            for page_number, image in images:
                patches_stored = self._process_single_page(doc_id, page_number, image)
                total_patches += patches_stored
                logger.debug(f"Page {page_number}: stored {patches_stored} patches")
        except Exception:
            logger.error(f"Ingestion failed at page processing, rolling back doc_id={doc_id}")
            self._rollback(doc_id)
            raise

        return total_patches

    def _process_single_page(
        self,
        doc_id: str,
        page_number: int,
        image: Image.Image,
    ) -> int:
        embeddings = self.embedding_service.encode_images([image])
        page_embeddings = embeddings[0]

        num_patches = page_embeddings.shape[0]

        self.milvus_service.insert_page_embeddings(
            doc_id=doc_id,
            page_number=page_number,
            embeddings=page_embeddings,
        )

        return num_patches

    def _rollback(self, doc_id: str) -> None:
        try:
            deleted = self.milvus_service.delete_document(doc_id)
            logger.info(f"Rollback complete: deleted {deleted} patches for doc_id={doc_id}")
        except Exception as e:
            logger.error(f"Rollback failed for doc_id={doc_id}: {e}")


async def save_upload_to_temp(file: UploadFile, temp_dir: Path) -> Path:
    if not file.filename:
        raise ValueError("No filename provided")

    validate_filename(file.filename)

    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"ingest_{file.filename}"

    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    logger.debug(f"Saved upload to temp: {temp_path}")
    return temp_path


async def ingest_uploaded_pdf(
    file: UploadFile,
    temp_dir: Path,
    doc_id: str | None = None,
    dpi: int = 144,
    max_pages: int | None = None,
) -> tuple[str, int, int]:
    temp_path = await save_upload_to_temp(file, temp_dir)

    try:
        service = IngestionService()
        return service.ingest_pdf_from_path(
            pdf_path=temp_path,
            doc_id=doc_id,
            dpi=dpi,
            max_pages=max_pages,
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()
            logger.debug(f"Cleaned up temp file: {temp_path}")


def get_ingestion_service() -> IngestionService:
    return IngestionService()
