import pytest
import torch
from PIL import Image

from src.services.embedding_service import EmbeddingService


@pytest.fixture
def embedding_service():
    return EmbeddingService()


@pytest.fixture
def sample_images():
    return [
        Image.new("RGB", (224, 224), color=(255, 0, 0)),
        Image.new("RGB", (224, 224), color=(0, 255, 0)),
    ]


@pytest.fixture
def single_image():
    return [Image.new("RGB", (224, 224), color=(100, 100, 100))]


@pytest.mark.integration
def test_encode_images_returns_tensor(embedding_service, sample_images):
    embeddings = embedding_service.encode_images(sample_images)

    assert isinstance(embeddings, torch.Tensor)
    assert embeddings.dtype == torch.bfloat16
    assert len(embeddings.shape) == 3
    assert embeddings.shape[0] == len(sample_images)


@pytest.mark.integration
def test_encode_images_output_dimensions(embedding_service, single_image):
    embeddings = embedding_service.encode_images(single_image)

    assert embeddings.shape[0] == 1
    assert embeddings.shape[2] == 128


@pytest.mark.integration
def test_encode_images_empty_list(embedding_service):
    with pytest.raises(ValueError, match="Images list cannot be empty"):
        embedding_service.encode_images([])


@pytest.mark.integration
def test_encode_query_returns_tensor(embedding_service):
    query = "What is the main topic of this document?"
    embeddings = embedding_service.encode_query(query)

    assert isinstance(embeddings, torch.Tensor)
    assert embeddings.dtype == torch.bfloat16
    assert len(embeddings.shape) == 3
    assert embeddings.shape[0] == 1


@pytest.mark.integration
def test_encode_query_output_dimensions(embedding_service):
    query = "Test query"
    embeddings = embedding_service.encode_query(query)

    assert embeddings.shape[2] == 128


@pytest.mark.integration
def test_encode_query_empty_string(embedding_service):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        embedding_service.encode_query("")


@pytest.mark.integration
def test_encode_query_whitespace_only(embedding_service):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        embedding_service.encode_query("   ")


@pytest.mark.integration
def test_encode_images_batch_returns_list(embedding_service, sample_images):
    batch_size = 1
    embeddings_list = embedding_service.encode_images_batch(sample_images, batch_size)

    assert isinstance(embeddings_list, list)
    assert len(embeddings_list) == 2


@pytest.mark.integration
def test_encode_images_batch_correct_batch_size(embedding_service):
    images = [Image.new("RGB", (224, 224), color=(i, i, i)) for i in range(5)]
    batch_size = 2

    embeddings_list = embedding_service.encode_images_batch(images, batch_size)

    assert len(embeddings_list) == 3
    assert embeddings_list[0].shape[0] == 2
    assert embeddings_list[1].shape[0] == 2
    assert embeddings_list[2].shape[0] == 1


@pytest.mark.integration
def test_encode_images_batch_invalid_batch_size(embedding_service, sample_images):
    with pytest.raises(ValueError, match="Batch size must be positive"):
        embedding_service.encode_images_batch(sample_images, 0)


@pytest.mark.integration
def test_encode_images_batch_empty_list(embedding_service):
    with pytest.raises(ValueError, match="Images list cannot be empty"):
        embedding_service.encode_images_batch([], 2)
