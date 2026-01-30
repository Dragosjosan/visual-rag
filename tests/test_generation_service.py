import httpx
import pytest
from PIL import Image

from app.services.generation_service import GenerationService, get_generation_service


def is_ollama_available() -> bool:
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


class TestGenerationService:
    @pytest.fixture
    def service(self) -> GenerationService:
        return GenerationService()

    @pytest.fixture
    def sample_image(self) -> Image.Image:
        img = Image.new("RGB", (100, 100), color="white")
        return img

    def test_image_to_base64(self, service: GenerationService, sample_image: Image.Image) -> None:
        result = service._image_to_base64(sample_image)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_answer_empty_query_raises(
        self, service: GenerationService, sample_image: Image.Image
    ) -> None:
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await service.generate_answer("", [sample_image])

    @pytest.mark.asyncio
    async def test_generate_answer_no_images_raises(self, service: GenerationService) -> None:
        with pytest.raises(ValueError, match="At least one image is required"):
            await service.generate_answer("What is this?", [])

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.skipif(not is_ollama_available(), reason="Ollama not available")
    async def test_generate_answer_with_ollama(self, service: GenerationService, sample_image: Image.Image) -> None:
        try:
            answer = await service.generate_answer(
                query="Describe what you see in this image.",
                images=[sample_image],
            )
            assert isinstance(answer, str)
            assert len(answer) > 0
        finally:
            await service.close()


def test_get_generation_service_singleton() -> None:
    service1 = get_generation_service()
    service2 = get_generation_service()
    assert service1 is service2
