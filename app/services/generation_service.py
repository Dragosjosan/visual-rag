import base64
import io
from pathlib import Path

import httpx
from loguru import logger
from PIL import Image

from app.core.config import settings

PROMPT_TEMPLATE = """You are a helpful assistant that answers questions based on the provided document images.

Question: {query}

Please analyze the document images and provide a clear, accurate answer based solely on the information \
visible in the images. If the answer cannot be found in the images, say so."""


class GenerationService:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=settings.ollama_base_url,
                timeout=httpx.Timeout(settings.vlm_timeout_seconds),
            )
        return self._client

    def _image_to_base64(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    def _load_image_from_path(self, path: Path | str) -> Image.Image:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        return Image.open(path).convert("RGB")

    async def generate_answer(
        self,
        query: str,
        images: list[Image.Image | Path | str],
        model: str | None = None,
    ) -> str:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not images:
            raise ValueError("At least one image is required")

        model = model or settings.vlm_model_name
        prompt = PROMPT_TEMPLATE.format(query=query)

        base64_images = []
        for img in images:
            if isinstance(img, (Path, str)):
                img = self._load_image_from_path(img)
            base64_images.append(self._image_to_base64(img))

        logger.info(f"Generating answer: query='{query[:50]}...', images={len(base64_images)}, model={model}")

        payload = {
            "model": model,
            "prompt": prompt,
            "images": base64_images,
            "stream": False,
        }

        try:
            client = await self._get_client()
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()

            result = response.json()
            answer = result.get("response", "")

            logger.info(f"Generation completed: {len(answer)} characters")
            return answer

        except httpx.TimeoutException as exc:
            logger.error(f"Ollama request timed out after {settings.vlm_timeout_seconds}s")
            raise TimeoutError(f"Generation timed out after {settings.vlm_timeout_seconds} seconds") from exc

        except httpx.HTTPStatusError as exc:
            logger.error(f"Ollama returned error: {exc.response.status_code}")
            raise RuntimeError(f"Ollama API error: {exc.response.status_code} - {exc.response.text}") from exc

        except Exception as exc:
            logger.opt(exception=exc).error("Failed to generate answer")
            raise RuntimeError(f"Failed to generate answer: {exc}") from exc

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("Closed generation service HTTP client")


_generation_service: GenerationService | None = None


def get_generation_service() -> GenerationService:
    global _generation_service
    if _generation_service is None:
        _generation_service = GenerationService()
    return _generation_service
