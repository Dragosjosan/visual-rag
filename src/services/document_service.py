from pathlib import Path

from fastapi import UploadFile
from loguru import logger

from src.models.document import DocumentInfo, validate_filename
from src.services.milvus_service import get_milvus_service
from src.services.pdf_processor import count_pdf_pages, generate_doc_id, process_pdf_document


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
) -> tuple[str, Path, int]:
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

        logger.info(f"Processed document: doc_id={doc_id}, doc_name={doc_name}, pages={page_count}")

        return doc_id, saved_pdf_path, page_count

    except Exception as exc:
        logger.opt(exception=exc).error("Failed to process uploaded document")
        raise ValueError(f"Failed to process uploaded document: {exc}") from exc


async def handle_document_upload(
    file: UploadFile,
    data_dir: Path,
    dpi: int = 144,
) -> tuple[str, str, Path, int]:
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


def delete_document(doc_name: str, data_dir: Path) -> tuple[str, int]:
    doc_path = data_dir / "documents" / doc_name / "original.pdf"

    if not doc_path.exists():
        raise FileNotFoundError(f"Document '{doc_name}' not found")

    doc_id = generate_doc_id(doc_path)

    milvus_service = get_milvus_service()
    patches_deleted = milvus_service.delete_document(doc_id)

    logger.info(f"Deleted document: doc_name={doc_name}, doc_id={doc_id}, patches={patches_deleted}")

    return doc_id, patches_deleted


def list_documents(data_dir: Path) -> list[DocumentInfo]:
    documents_dir = data_dir / "documents"
    if not documents_dir.exists():
        return []

    documents = []
    for doc_path in documents_dir.iterdir():
        if not doc_path.is_dir():
            continue

        doc_name = doc_path.name
        pdf_path = doc_path / "original.pdf"

        if not pdf_path.exists():
            logger.warning(f"No original.pdf found for {doc_name}")
            continue

        try:
            doc_id = generate_doc_id(pdf_path)
            page_count = count_pdf_pages(pdf_path)
            documents.append(
                DocumentInfo(
                    doc_id=doc_id,
                    doc_name=doc_name,
                    page_count=page_count,
                    pdf_path=str(pdf_path),
                )
            )
        except Exception as exc:
            logger.opt(exception=exc).warning(f"Failed to get info for {doc_name}")

    logger.info(f"Listed {len(documents)} documents")
    return documents


def get_document_by_name(doc_name: str, data_dir: Path) -> DocumentInfo:
    pdf_path = data_dir / "documents" / doc_name / "original.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(f"Document '{doc_name}' not found")

    doc_id = generate_doc_id(pdf_path)
    page_count = count_pdf_pages(pdf_path)

    return DocumentInfo(
        doc_id=doc_id,
        doc_name=doc_name,
        page_count=page_count,
        pdf_path=str(pdf_path),
    )


def get_document_by_id(doc_id: str, data_dir: Path) -> DocumentInfo:
    documents_dir = data_dir / "documents"
    if not documents_dir.exists():
        raise FileNotFoundError(f"Document with id '{doc_id}' not found")

    for doc_path in documents_dir.iterdir():
        if not doc_path.is_dir():
            continue

        doc_name = doc_path.name
        pdf_path = doc_path / "original.pdf"

        if not pdf_path.exists():
            continue

        try:
            current_doc_id = generate_doc_id(pdf_path)
            if current_doc_id == doc_id:
                page_count = count_pdf_pages(pdf_path)
                return DocumentInfo(
                    doc_id=doc_id,
                    doc_name=doc_name,
                    page_count=page_count,
                    pdf_path=str(pdf_path),
                )
        except Exception as exc:
            logger.opt(exception=exc).warning(f"Failed to check doc_id for {doc_name}")

    raise FileNotFoundError(f"Document with id '{doc_id}' not found")
