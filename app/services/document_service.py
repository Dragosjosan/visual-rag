from pathlib import Path
from typing import Tuple

from fastapi import UploadFile
from loguru import logger

from app.models.document import validate_filename
from app.services.pdf_processor import process_pdf_document


async def save_uploaded_file(file: UploadFile, temp_dir: Path) -> Path:
    try:
        if not file.filename:
            raise ValueError("No filename provided")

        validate_filename(file.filename)

        temp_path = temp_dir / f"temp_{file.filename}"

        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        logger.info(f"Saved uploaded file to {temp_path}")
        return temp_path
    except Exception as exc:
        logger.opt(exception=exc).error("Failed to save uploaded file")
        raise ValueError(f"Failed to save uploaded file: {exc}") from exc


def process_uploaded_document(
    pdf_path: Path,
    output_dir: Path,
    doc_name: str,
    dpi: int = 144,
    use_parallel: bool = True,
    max_workers: int = 4,
) -> Tuple[str, Path, int]:
    try:
        doc_id, saved_pdf_path, image_paths, images = process_pdf_document(
            pdf_path=pdf_path,
            output_dir=output_dir,
            doc_name=doc_name,
            dpi=dpi,
            save_pdf=True,
            save_images_flag=True,
            use_parallel=use_parallel,
            max_workers=max_workers,
        )

        page_count = len(images)

        logger.info(
            f"Processed document: doc_id={doc_id}, "
            f"doc_name={doc_name}, pages={page_count}"
        )

        return doc_id, saved_pdf_path, page_count

    except Exception as exc:
        logger.opt(exception=exc).error("Failed to process uploaded document")
        raise ValueError(f"Failed to process uploaded document: {exc}") from exc


async def handle_document_upload(
    file: UploadFile,
    data_dir: Path,
    dpi: int = 144,
) -> Tuple[str, str, Path, int]:
    try:
        if not file.filename:
            raise ValueError("No filename provided")

        validate_filename(file.filename)

        doc_name = Path(file.filename).stem

        temp_pdf_path = await save_uploaded_file(file, data_dir)

        try:
            doc_id, saved_pdf_path, page_count = process_uploaded_document(
                pdf_path=temp_pdf_path,
                output_dir=data_dir,
                doc_name=doc_name,
                dpi=dpi,
                use_parallel=True,
                max_workers=4,
            )

            return doc_id, doc_name, saved_pdf_path, page_count

        finally:
            if temp_pdf_path.exists():
                temp_pdf_path.unlink()
                logger.debug(f"Cleaned up temporary file: {temp_pdf_path}")

    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to handle document upload: {file.filename}")
        raise ValueError(f"Failed to handle document upload: {exc}") from exc
