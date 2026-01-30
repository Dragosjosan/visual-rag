import tempfile
from pathlib import Path

import pytest
from PIL import Image

from app.services.pdf_processor import (
    convert_pdf_to_images,
    convert_pdf_to_images_parallel,
    generate_doc_id,
    process_pdf_document,
    save_images,
    save_pdf_document,
)


@pytest.fixture
def colpali_pdf():
    pdf_path = Path(__file__).parent.parent.parent / "docs" / "2407.01449v6.pdf"
    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")
    return pdf_path


def test_generate_doc_id(colpali_pdf):
    doc_id = generate_doc_id(colpali_pdf)

    assert isinstance(doc_id, str)
    assert len(doc_id) == 64

    doc_id_2 = generate_doc_id(colpali_pdf)
    assert doc_id == doc_id_2


def test_generate_doc_id_file_not_found():
    with pytest.raises(ValueError, match="Failed to generate doc_id"):
        generate_doc_id("/nonexistent/file.pdf")


def test_convert_pdf_to_images_first_page(colpali_pdf):
    results = convert_pdf_to_images(colpali_pdf, dpi=144)

    assert isinstance(results, list)
    assert len(results) > 0

    first_page_num, first_image = results[0]
    assert first_page_num == 1
    assert isinstance(first_image, Image.Image)
    assert first_image.mode == "RGB"


def test_convert_pdf_to_images_page_numbers_1_indexed(colpali_pdf):
    results = convert_pdf_to_images(colpali_pdf, dpi=72)

    assert len(results) > 0

    for page_num, image in results:
        assert isinstance(page_num, int)
        assert page_num >= 1
        assert isinstance(image, Image.Image)
        assert image.mode == "RGB"

    first_page_num = results[0][0]
    assert first_page_num == 1


def test_convert_pdf_to_images_rgb_format(colpali_pdf):
    results = convert_pdf_to_images(colpali_pdf, dpi=72)

    for _, image in results:
        assert image.mode == "RGB"


def test_convert_pdf_to_images_with_save(colpali_pdf):
    with tempfile.TemporaryDirectory() as tmpdir:
        results = convert_pdf_to_images(colpali_pdf, dpi=72, output_dir=tmpdir)

        assert len(results) > 0

        doc_images_dir = Path(tmpdir) / "images" / "2407.01449v6"
        assert doc_images_dir.exists()

        saved_files = list(doc_images_dir.glob("*.png"))
        assert len(saved_files) == len(results)

        for saved_file in saved_files:
            assert saved_file.name.startswith("page_")
            assert saved_file.suffix == ".png"


def test_convert_pdf_to_images_invalid_dpi(colpali_pdf):
    with pytest.raises(ValueError, match="DPI must be positive"):
        convert_pdf_to_images(colpali_pdf, dpi=0)


def test_convert_pdf_to_images_file_not_found():
    with pytest.raises(ValueError, match="Failed to convert PDF"):
        convert_pdf_to_images("/nonexistent/file.pdf")


def test_convert_pdf_to_images_not_pdf(tmp_path):
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("not a pdf")

    with pytest.raises(ValueError, match="File must be a PDF"):
        convert_pdf_to_images(txt_file)


def test_convert_pdf_to_images_parallel_first_page(colpali_pdf):
    results = convert_pdf_to_images_parallel(colpali_pdf, dpi=72, max_workers=2)

    assert isinstance(results, list)
    assert len(results) > 0

    first_page_num, first_image = results[0]
    assert first_page_num == 1
    assert isinstance(first_image, Image.Image)
    assert first_image.mode == "RGB"


def test_convert_pdf_to_images_parallel_sorted(colpali_pdf):
    results = convert_pdf_to_images_parallel(colpali_pdf, dpi=72, max_workers=2)

    assert len(results) > 0

    page_numbers = [page_num for page_num, _ in results]
    assert page_numbers == sorted(page_numbers)
    assert page_numbers[0] == 1


def test_save_images(tmp_path):
    test_images = [
        (1, Image.new("RGB", (100, 100), color=(255, 0, 0))),
        (2, Image.new("RGB", (100, 100), color=(0, 255, 0))),
        (3, Image.new("RGB", (100, 100), color=(0, 0, 255))),
    ]

    saved_paths = save_images(test_images, tmp_path, "test_doc", format="PNG")

    assert len(saved_paths) == 3

    doc_images_dir = tmp_path / "images" / "test_doc"
    assert doc_images_dir.exists()

    for i, path in enumerate(saved_paths, start=1):
        assert path.exists()
        assert path.name == f"page_{i:02d}.png"

        image = Image.open(path)
        assert image.mode == "RGB"
        assert image.size == (100, 100)


def test_save_pdf_document(colpali_pdf, tmp_path):
    saved_path = save_pdf_document(colpali_pdf, tmp_path, "colpali_paper")

    assert saved_path.exists()
    assert saved_path.name == "original.pdf"
    assert saved_path.parent.name == "colpali_paper"
    assert saved_path.parent.parent.name == "documents"


def test_process_pdf_document(colpali_pdf, tmp_path):
    doc_id, pdf_path, image_paths, images = process_pdf_document(
        colpali_pdf,
        tmp_path,
        doc_name="colpali_paper",
        dpi=72,
        save_pdf=True,
        save_images_flag=True,
    )

    assert isinstance(doc_id, str)
    assert len(doc_id) == 64

    assert pdf_path is not None
    assert pdf_path.exists()
    assert pdf_path == tmp_path / "documents" / "colpali_paper" / "original.pdf"

    assert len(image_paths) == len(images)
    assert len(images) > 0

    for image_path in image_paths:
        assert image_path.exists()
        assert image_path.parent == tmp_path / "images" / "colpali_paper"

    for page_num, image in images:
        assert page_num >= 1
        assert image.mode == "RGB"


def test_process_pdf_document_without_saving(colpali_pdf, tmp_path):
    doc_id, pdf_path, image_paths, images = process_pdf_document(
        colpali_pdf,
        tmp_path,
        dpi=72,
        save_pdf=False,
        save_images_flag=False,
    )

    assert isinstance(doc_id, str)
    assert pdf_path is None
    assert len(image_paths) == 0
    assert len(images) > 0
