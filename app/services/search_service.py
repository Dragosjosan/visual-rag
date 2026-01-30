import time

from loguru import logger

from app.models.document import SearchResponse, SearchResult
from app.services.retrieval_service import RetrievalService, get_retrieval_service


class SearchService:
    def __init__(self, retrieval_service: RetrievalService | None = None) -> None:
        self._retrieval_service = retrieval_service

    @property
    def retrieval_service(self) -> RetrievalService:
        if self._retrieval_service is None:
            self._retrieval_service = get_retrieval_service()
        return self._retrieval_service

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_id_filter: str | None = None,
    ) -> SearchResponse:
        start_time = time.perf_counter()

        results = self.retrieval_service.retrieve(
            query=query,
            top_k=top_k,
            doc_id_filter=doc_id_filter,
        )

        search_results = [
            SearchResult(
                doc_id=r.doc_id,
                page_number=r.page_number,
                score=r.score,
            )
            for r in results
        ]

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(f"Search completed: query='{query}', results={len(search_results)}, time={elapsed_ms:.2f}ms")

        return SearchResponse(
            query=query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(elapsed_ms, 2),
        )


_search_service: SearchService | None = None


def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
