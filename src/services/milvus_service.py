from typing import Any

import torch
from loguru import logger
from pymilvus import DataType, MilvusClient

from src.core.config import settings


class MilvusService:
    EMBEDDING_DIM = 128
    MAX_PATCHES_PER_PAGE = 1030

    def __init__(self) -> None:
        self._client: MilvusClient | None = None

    def _get_client(self) -> MilvusClient:
        if self._client is None:
            uri = f"http://{settings.milvus_host}:{settings.milvus_port}"
            self._client = MilvusClient(uri=uri)
            logger.info(f"Connected to Milvus at {uri}")
        return self._client

    def _ensure_collection(self) -> None:
        client = self._get_client()
        collection_name = settings.milvus_collection_name

        if client.has_collection(collection_name):
            logger.info(f"Collection {collection_name} already exists")
            load_state = client.get_load_state(collection_name=collection_name)
            if load_state.get("state") != "Loaded":
                client.load_collection(collection_name=collection_name)
                logger.info(f"Loaded collection: {collection_name}")
            else:
                logger.info(f"Collection {collection_name} already loaded")
            return

        self._create_collection()

    def _create_collection(self) -> None:
        client = self._get_client()
        collection_name = settings.milvus_collection_name

        schema = client.create_schema(auto_id=True, enable_dynamic_fields=False)

        schema.add_field(
            field_name="patch_id",
            datatype=DataType.INT64,
            is_primary=True,
            auto_id=True,
        )
        schema.add_field(
            field_name="doc_id",
            datatype=DataType.VARCHAR,
            max_length=64,
        )
        schema.add_field(
            field_name="page_number",
            datatype=DataType.INT32,
        )
        schema.add_field(
            field_name="patch_index",
            datatype=DataType.INT32,
        )
        schema.add_field(
            field_name="embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim=self.EMBEDDING_DIM,
        )

        client.create_collection(collection_name=collection_name, schema=schema)
        logger.info(f"Created collection: {collection_name}")

        self._create_indexes()

    def _create_indexes(self) -> None:
        client = self._get_client()
        collection_name = settings.milvus_collection_name

        index_params = client.prepare_index_params()

        index_params.add_index(
            field_name="embedding",
            index_type="HNSW",
            metric_type="IP",
            params={"M": 16, "efConstruction": 256},
        )

        index_params.add_index(
            field_name="doc_id",
            index_type="Trie",
        )

        client.create_index(collection_name=collection_name, index_params=index_params)
        logger.info("Created HNSW index on embedding")

        client.load_collection(collection_name=collection_name)
        logger.info(f"Loaded collection: {collection_name}")

    def insert_page_embeddings(
        self,
        doc_id: str,
        page_number: int,
        embeddings: torch.Tensor,
    ) -> int:
        self._ensure_collection()
        client = self._get_client()

        if embeddings.dim() != 2:
            raise ValueError(f"Expected 2D tensor, got {embeddings.dim()}D")

        num_patches = embeddings.shape[0]
        embedding_dim = embeddings.shape[1]

        if embedding_dim != self.EMBEDDING_DIM:
            raise ValueError(f"Expected embedding dim {self.EMBEDDING_DIM}, got {embedding_dim}")

        if num_patches > self.MAX_PATCHES_PER_PAGE:
            logger.warning(f"Truncating patches from {num_patches} to {self.MAX_PATCHES_PER_PAGE}")
            embeddings = embeddings[: self.MAX_PATCHES_PER_PAGE]
            num_patches = self.MAX_PATCHES_PER_PAGE

        embeddings_list = embeddings.cpu().float().numpy().tolist()

        data = [
            {
                "doc_id": doc_id,
                "page_number": page_number,
                "patch_index": i,
                "embedding": emb,
            }
            for i, emb in enumerate(embeddings_list)
        ]

        client.insert(collection_name=settings.milvus_collection_name, data=data)
        logger.info(f"Inserted {num_patches} patches for doc={doc_id}, page={page_number}")

        return num_patches

    def search_pages(
        self,
        query_embeddings: torch.Tensor,
        top_k: int = 10,
        doc_id_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        self._ensure_collection()
        client = self._get_client()

        try:
            client.flush(collection_name=settings.milvus_collection_name)
        except Exception as exc:
            logger.opt(exception=exc).error("Flush failed during search")

        if query_embeddings.dim() == 1:
            query_embeddings = query_embeddings.unsqueeze(0)

        query_list = query_embeddings.cpu().float().numpy().tolist()

        search_params = {
            "metric_type": "IP",
            "params": {"ef": 64},
        }

        expr = None
        if doc_id_filter:
            expr = f'doc_id == "{doc_id_filter}"'

        page_scores: dict[tuple[str, int], float] = {}

        for query_vector in query_list:
            results = client.search(
                collection_name=settings.milvus_collection_name,
                data=[query_vector],
                anns_field="embedding",
                search_params=search_params,
                limit=100,
                filter=expr,
                output_fields=["doc_id", "page_number"],
            )

            for hits in results:
                for hit in hits:
                    doc_id = hit["entity"].get("doc_id")
                    page_number = hit["entity"].get("page_number")
                    score = hit["distance"]
                    key = (doc_id, page_number)

                    if score > page_scores.get(key, float("-inf")):
                        page_scores[key] = score

        aggregated = [
            {"doc_id": doc_id, "page_number": page_number, "score": score}
            for (doc_id, page_number), score in page_scores.items()
        ]
        aggregated.sort(key=lambda x: x["score"], reverse=True)

        matches = aggregated[:top_k]
        logger.info(f"Search returned {len(matches)} page results")
        return matches

    def delete_document(self, doc_id: str) -> int:
        self._ensure_collection()
        client = self._get_client()

        try:
            client.flush(collection_name=settings.milvus_collection_name)
        except Exception as exc:
            logger.opt(exception=exc).error("Flush failed before delete")

        expr = f'doc_id == "{doc_id}"'
        result = client.delete(collection_name=settings.milvus_collection_name, filter=expr)

        delete_count = result.get("delete_count", 0)
        logger.info(f"Deleted {delete_count} pages for doc={doc_id}")

        try:
            client.flush(collection_name=settings.milvus_collection_name)
        except Exception as exc:
            logger.opt(exception=exc).error("Flush failed after delete")

        return delete_count

    def get_collection_stats(self) -> dict[str, Any]:
        self._ensure_collection()
        client = self._get_client()

        stats = client.get_collection_stats(collection_name=settings.milvus_collection_name)
        return stats

    def drop_collection(self) -> None:
        client = self._get_client()
        collection_name = settings.milvus_collection_name

        if client.has_collection(collection_name):
            client.drop_collection(collection_name)
            logger.info(f"Dropped collection: {collection_name}")

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("Disconnected from Milvus")


_milvus_service: MilvusService | None = None


def get_milvus_service() -> MilvusService:
    global _milvus_service
    if _milvus_service is None:
        _milvus_service = MilvusService()
    return _milvus_service
