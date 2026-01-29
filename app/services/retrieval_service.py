from typing import Any

from loguru import logger
from pydantic import BaseModel

from app.core.config import settings
from app.services.embedding_service import get_embedding_service
from app.services.milvus_service import get_milvus_service


class RetrievalResult(BaseModel):
    doc_id: str
    page_number: int
    score: float


class RetrievalService:
    def __init__(self) -> None:
        self._embedding_service = get_embedding_service()
        self._milvus_service = get_milvus_service()

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        doc_id_filter: str | None = None,
    ) -> list[RetrievalResult]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k is None:
            top_k = settings.top_k

        logger.info(f"Retrieving top {top_k} pages for query: {query}")

        query_embeddings = self._embedding_service.encode_query(query)
        logger.debug(f"Query embeddings shape: {query_embeddings.shape}")

        if query_embeddings.dim() == 3:
            query_embeddings = query_embeddings.squeeze(0)

        raw_results = self._milvus_service.search_pages(
            query_embeddings=query_embeddings,
            top_k=top_k,
            doc_id_filter=doc_id_filter,
        )

        results = [
            RetrievalResult(
                doc_id=r["doc_id"],
                page_number=r["page_number"],
                score=r["score"],
            )
            for r in raw_results
        ]

        logger.info(f"Retrieved {len(results)} pages")
        return results

    def retrieve_raw(
        self,
        query: str,
        top_k: int | None = None,
        doc_id_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k is None:
            top_k = settings.top_k

        query_embeddings = self._embedding_service.encode_query(query)

        if query_embeddings.dim() == 3:
            query_embeddings = query_embeddings.squeeze(0)

        return self._milvus_service.search_pages(
            query_embeddings=query_embeddings,
            top_k=top_k,
            doc_id_filter=doc_id_filter,
        )


_retrieval_service: RetrievalService | None = None


def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
