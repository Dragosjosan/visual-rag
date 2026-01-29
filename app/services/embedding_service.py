from typing import List

import torch
from loguru import logger
from PIL import Image

from app.core.model_loader import get_model_loader


class EmbeddingService:
    def __init__(self) -> None:
        self._loader = get_model_loader()

    def encode_images(self, images: List[Image.Image]) -> torch.Tensor:
        if not images:
            raise ValueError("Images list cannot be empty")

        try:
            logger.info(f"Encoding {len(images)} images")

            model = self._loader.model
            processor = self._loader.processor

            batch_images = processor.process_images(images).to(model.device)

            with torch.no_grad():
                image_embeddings = model(**batch_images)

            logger.success(f"Generated embeddings with shape: {image_embeddings.shape}")
            return image_embeddings

        except Exception as e:
            logger.error(f"Failed to encode images: {e}")
            raise

    def encode_query(self, query: str) -> torch.Tensor:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            logger.info(f"Encoding query: {query}")

            model = self._loader.model
            processor = self._loader.processor

            batch_query = processor.process_queries([query]).to(model.device)

            with torch.no_grad():
                query_embeddings = model(**batch_query)

            logger.success(f"Generated query embeddings with shape: {query_embeddings.shape}")
            return query_embeddings

        except Exception as e:
            logger.error(f"Failed to encode query: {e}")
            raise

    def encode_images_batch(
        self, images: List[Image.Image], batch_size: int
    ) -> List[torch.Tensor]:
        if not images:
            raise ValueError("Images list cannot be empty")

        if batch_size <= 0:
            raise ValueError("Batch size must be positive")

        try:
            embeddings_list = []

            for i in range(0, len(images), batch_size):
                batch = images[i : i + batch_size]
                logger.info(f"Processing batch {i // batch_size + 1}: {len(batch)} images")

                batch_embeddings = self.encode_images(batch)
                embeddings_list.append(batch_embeddings)

            return embeddings_list

        except Exception as e:
            logger.error(f"Failed to encode images in batches: {e}")
            raise


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
