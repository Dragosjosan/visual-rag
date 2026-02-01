import hashlib
import io
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pymupdf
from loguru import logger
from PIL import Image


def generate_doc_id(file_path: str | Path) -> str:
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        doc_id = sha256_hash.hexdigest()
        logger.info(f"Generated doc_id: {doc_id} for file: {file_path}")
        return doc_id
    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to generate doc_id for {file_path}")
        raise ValueError(f"Failed to generate doc_id: {exc}") from exc


def count_pdf_pages(file_path: str | Path) -> int:
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        pdf_document = pymupdf.open(file_path)
        page_count = len(pdf_document)
        pdf_document.close()

        return page_count
    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to count pages for {file_path}")
        raise ValueError(f"Failed to count PDF pages: {exc}") from exc


def convert_pdf_to_images(
    file_path: str | Path,
    dpi: int = 144,
    thread_count: int | None = None,
    output_dir: str | Path | None = None,
    save_format: str = "PNG",
) -> list[tuple[int, Image.Image]]:
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.suffix.lower() == ".pdf":
            raise ValueError(f"File must be a PDF, got: {file_path.suffix}")

        if dpi <= 0:
            raise ValueError(f"DPI must be positive, got {dpi}")

        logger.info(f"Converting PDF to images: {file_path} with DPI={dpi}")

        zoom = dpi / 72
        matrix = pymupdf.Matrix(zoom, zoom)

        pdf_document = pymupdf.open(file_path)
        results = []

        try:
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=matrix)

                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))

                if image.mode != "RGB":
                    image = image.convert("RGB")

                results.append((page_num + 1, image))
        finally:
            pdf_document.close()

        if output_dir:
            doc_name = file_path.stem
            save_images(results, output_dir, doc_name, save_format)

        logger.info(f"Successfully converted PDF to {len(results)} images: {file_path}")
        return results

    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to convert PDF to images: {file_path}")
        raise ValueError(f"Failed to convert PDF to images: {exc}") from exc


def convert_pdf_to_images_parallel(
    file_path: str | Path,
    dpi: int = 144,
    max_workers: int = 4,
    output_dir: str | Path | None = None,
    save_format: str = "PNG",
) -> list[tuple[int, Image.Image]]:
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.suffix.lower() == ".pdf":
            raise ValueError(f"File must be a PDF, got: {file_path.suffix}")

        if dpi <= 0:
            raise ValueError(f"DPI must be positive, got {dpi}")

        if max_workers <= 0:
            raise ValueError(f"max_workers must be positive, got {max_workers}")

        logger.info(f"Converting PDF to images (parallel): {file_path} with DPI={dpi}, max_workers={max_workers}")

        zoom = dpi / 72
        matrix = pymupdf.Matrix(zoom, zoom)

        pdf_document = pymupdf.open(file_path)
        page_count = len(pdf_document)

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(_process_page, file_path, page_num, matrix): page_num + 1
                for page_num in range(page_count)
            }

            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    image = future.result()
                    results.append((page_num, image))
                except Exception as exc:
                    logger.opt(exception=exc).error(f"Failed to process page {page_num}")
                    raise

        pdf_document.close()

        results.sort(key=lambda x: x[0])

        if output_dir:
            doc_name = file_path.stem
            save_images(results, output_dir, doc_name, save_format)

        logger.info(f"Successfully converted PDF to {len(results)} images (parallel): {file_path}")
        return results

    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to convert PDF to images (parallel): {file_path}")
        raise ValueError(f"Failed to convert PDF to images: {exc}") from exc


def save_images(
    images: list[tuple[int, Image.Image]],
    output_dir: str | Path,
    doc_name: str,
    format: str = "PNG",
) -> list[Path]:
    try:
        images_dir = Path(output_dir) / "images" / doc_name
        images_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []
        for page_num, image in images:
            file_name = f"page_{page_num:02d}.{format.lower()}"
            file_path = images_dir / file_name

            image.save(file_path, format=format)
            saved_paths.append(file_path)

            logger.debug(f"Saved page {page_num} to {file_path}")

        logger.info(f"Saved {len(saved_paths)} images to {images_dir}")
        return saved_paths

    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to save images to {output_dir}")
        raise ValueError(f"Failed to save images: {exc}") from exc


def save_pdf_document(
    pdf_path: str | Path,
    output_dir: str | Path,
    doc_name: str,
) -> Path:
    try:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        documents_dir = Path(output_dir) / "documents" / doc_name
        documents_dir.mkdir(parents=True, exist_ok=True)

        dest_path = documents_dir / "original.pdf"
        shutil.copy2(pdf_path, dest_path)

        logger.info(f"Saved PDF document to {dest_path}")
        return dest_path

    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to save PDF document to {output_dir}")
        raise ValueError(f"Failed to save PDF document: {exc}") from exc


def process_pdf_document(
    pdf_path: str | Path,
    output_dir: str | Path,
    doc_name: str | None = None,
    dpi: int = 144,
    save_pdf: bool = True,
    save_images_flag: bool = True,
    use_parallel: bool = False,
    max_workers: int = 4,
) -> tuple[str, Path | None, list[Path], list[tuple[int, Image.Image]]]:
    try:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        if doc_name is None:
            doc_name = pdf_path.stem

        logger.info(f"Processing PDF document: {pdf_path} as '{doc_name}'")

        doc_id = generate_doc_id(pdf_path)

        saved_pdf_path = None
        if save_pdf:
            saved_pdf_path = save_pdf_document(pdf_path, output_dir, doc_name)

        if use_parallel:
            images = convert_pdf_to_images_parallel(pdf_path, dpi=dpi, max_workers=max_workers)
        else:
            images = convert_pdf_to_images(pdf_path, dpi=dpi)

        saved_image_paths = []
        if save_images_flag:
            saved_image_paths = save_images(images, output_dir, doc_name)

        logger.info(f"Successfully processed PDF: {len(images)} pages, doc_id: {doc_id}, doc_name: {doc_name}")

        return doc_id, saved_pdf_path, saved_image_paths, images

    except Exception as exc:
        logger.opt(exception=exc).error(f"Failed to process PDF document: {pdf_path}")
        raise ValueError(f"Failed to process PDF document: {exc}") from exc


def _process_page(
    file_path: Path,
    page_num: int,
    matrix: pymupdf.Matrix,
) -> Image.Image:
    pdf_document = pymupdf.open(file_path)
    try:
        page = pdf_document[page_num]
        pix = page.get_pixmap(matrix=matrix)

        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))

        if image.mode != "RGB":
            image = image.convert("RGB")

        return image
    finally:
        pdf_document.close()
