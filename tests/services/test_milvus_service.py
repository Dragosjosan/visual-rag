import pytest
import torch

from src.services.milvus_service import MilvusService, get_milvus_service


@pytest.fixture
def milvus_service():
    service = MilvusService()
    yield service
    service.drop_collection()
    service.disconnect()


@pytest.fixture
def sample_embeddings():
    return torch.randn(1024, 128)


@pytest.fixture
def small_embeddings():
    return torch.randn(10, 128)


@pytest.mark.integration
def test_create_collection(milvus_service):
    milvus_service._ensure_collection()
    client = milvus_service._get_client()

    assert client.has_collection("visual_rag_patches")


@pytest.mark.integration
def test_collection_schema(milvus_service):
    milvus_service._ensure_collection()
    client = milvus_service._get_client()

    schema = client.describe_collection("visual_rag_patches")
    field_names = [field["name"] for field in schema["fields"]]

    assert "patch_id" in field_names
    assert "doc_id" in field_names
    assert "page_number" in field_names
    assert "patch_index" in field_names
    assert "embedding" in field_names


@pytest.mark.integration
def test_insert_page_embeddings(milvus_service, sample_embeddings):
    doc_id = "test_doc_001"
    page_number = 1

    num_patches = milvus_service.insert_page_embeddings(doc_id, page_number, sample_embeddings)

    assert num_patches == 1024


@pytest.mark.integration
def test_insert_page_embeddings_wrong_dim(milvus_service):
    wrong_dim_embeddings = torch.randn(10, 64)

    with pytest.raises(ValueError, match="Expected embedding dim 128"):
        milvus_service.insert_page_embeddings("test_doc", 1, wrong_dim_embeddings)


@pytest.mark.integration
def test_insert_page_embeddings_wrong_tensor_shape(milvus_service):
    wrong_shape = torch.randn(128)

    with pytest.raises(ValueError, match="Expected 2D tensor"):
        milvus_service.insert_page_embeddings("test_doc", 1, wrong_shape)


@pytest.mark.integration
def test_search_pages(milvus_service, small_embeddings):
    doc_id = "search_test_doc"
    milvus_service.insert_page_embeddings(doc_id, 1, small_embeddings)

    query = small_embeddings[0]
    results = milvus_service.search_pages(query, top_k=5)

    assert len(results) > 0
    assert len(results) <= 5
    assert all("doc_id" in r for r in results)
    assert all("page_number" in r for r in results)
    assert all("score" in r for r in results)


@pytest.mark.integration
def test_search_pages_with_filter(milvus_service, small_embeddings):
    milvus_service.insert_page_embeddings("doc_a", 1, small_embeddings)
    milvus_service.insert_page_embeddings("doc_b", 1, small_embeddings)

    query = small_embeddings[0]
    results = milvus_service.search_pages(query, top_k=20, doc_id_filter="doc_a")

    assert len(results) > 0
    assert all(r["doc_id"] == "doc_a" for r in results)


@pytest.mark.integration
def test_query_specific_page(milvus_service, small_embeddings):
    doc_id = "get_test_doc"
    page_number = 2
    milvus_service.insert_page_embeddings(doc_id, page_number, small_embeddings)

    query = small_embeddings[0]
    results = milvus_service.search_pages(query, top_k=10, doc_id_filter=doc_id)

    assert len(results) > 0
    assert all(r["doc_id"] == doc_id for r in results)
    assert any(r["page_number"] == page_number for r in results)


@pytest.mark.integration
def test_query_nonexistent_document(milvus_service, small_embeddings):
    query = small_embeddings[0]
    results = milvus_service.search_pages(query, top_k=10, doc_id_filter="nonexistent_doc")

    assert len(results) == 0


@pytest.mark.integration
def test_delete_document(milvus_service, small_embeddings):
    doc_id = "delete_test_doc"
    milvus_service.insert_page_embeddings(doc_id, 1, small_embeddings)
    milvus_service.insert_page_embeddings(doc_id, 2, small_embeddings)

    delete_count = milvus_service.delete_document(doc_id)

    assert delete_count == 20

    query = small_embeddings[0]
    results = milvus_service.search_pages(query, top_k=10, doc_id_filter=doc_id)
    assert len(results) == 0


@pytest.mark.integration
def test_delete_document_nonexistent(milvus_service):
    delete_count = milvus_service.delete_document("nonexistent_doc")

    assert delete_count == 0


@pytest.mark.integration
def test_get_milvus_service_singleton():
    service1 = get_milvus_service()
    service2 = get_milvus_service()

    assert service1 is service2
