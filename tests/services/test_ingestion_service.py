from pathlib import Path

import pytest

from src.services.ingestion_service import IngestionService


@pytest.fixture
def ingestion_service():
    return IngestionService()


@pytest.fixture
def sample_pdf_path():
    return Path(__file__).parent.parent.parent / "docs" / "2407.01449v6.pdf"


@pytest.mark.integration
def test_ingest_pdf_file_not_found(ingestion_service):
    with pytest.raises(FileNotFoundError):
        ingestion_service.ingest_pdf_from_path(Path("/nonexistent/file.pdf"))


@pytest.mark.integration
def test_ingest_pdf_generates_doc_id(ingestion_service, sample_pdf_path):
    if not sample_pdf_path.exists():
        pytest.skip("Sample PDF not available")

    doc_id, pages, patches = ingestion_service.ingest_pdf_from_path(sample_pdf_path, max_pages=1)

    assert doc_id is not None
    assert len(doc_id) == 64
    assert pages == 1
    assert patches > 0


@pytest.mark.integration
def test_ingest_pdf_custom_doc_id(ingestion_service, sample_pdf_path):
    if not sample_pdf_path.exists():
        pytest.skip("Sample PDF not available")

    custom_id = "my-custom-doc-id"

    doc_id, pages, patches = ingestion_service.ingest_pdf_from_path(sample_pdf_path, doc_id=custom_id, max_pages=1)

    assert doc_id == custom_id
    assert pages == 1
    assert patches > 0
