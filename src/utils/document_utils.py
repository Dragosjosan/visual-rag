from pathlib import Path

from loguru import logger

from src.services.pdf_processor import generate_doc_id


def get_doc_id_to_name_mapping(data_dir: Path) -> dict[str, str]:
    documents_dir = data_dir / "documents"
    if not documents_dir.exists():
        logger.warning(f"Documents directory does not exist: {documents_dir}")
        return {}

    mapping = {}
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
            mapping[doc_id] = doc_name
        except Exception as exc:
            logger.opt(exception=exc).warning(f"Failed to generate doc_id for {doc_name}")

    logger.info(f"Built doc_id to doc_name mapping: {len(mapping)} documents")
    return mapping


def get_page_image_path(data_dir: Path, doc_name: str, page_number: int) -> Path:
    return data_dir / "images" / doc_name / f"page_{page_number:02d}.png"
