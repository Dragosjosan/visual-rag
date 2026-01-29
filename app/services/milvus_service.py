from typing import Any

import torch
from loguru import logger
from pymilvus import DataType, MilvusClient

from app.core.config import settings


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
            return

        self._create_collection()

    def _create_collection(self) -> None:
        client = self._get_client()
        collection_name = settings.milvus_collection_name

        schema = client.create_schema(auto_id=True, enable_dynamic_fields=False)

        schema.add_field(
            field_name="page_id",
            datatype=DataType.INT64,
            is_primary=True,
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

        struct_schema = client.create_struct_field_schema()
        struct_schema.add_field(
            field_name="embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim=self.EMBEDDING_DIM,
        )

        schema.add_field(
            field_name="patches",
            datatype=DataType.ARRAY,
            element_type=DataType.STRUCT,
            struct_schema=struct_schema,
            max_capacity=self.MAX_PATCHES_PER_PAGE,
        )

        client.create_collection(collection_name=collection_name, schema=schema)
        logger.info(f"Created collection: {collection_name}")

        self._create_indexes()

    def _create_indexes(self) -> None:
        client = self._get_client()
        collection_name = settings.milvus_collection_name

        index_params = client.prepare_index_params()

        index_params.add_index(
            field_name="patches[embedding]",
            index_type="HNSW",
            metric_type="MAX_SIM_IP",
            params={"M": 16, "efConstruction": 256},
        )

        index_params.add_index(
            field_name="doc_id",
            index_type="Trie",
        )

        client.create_index(collection_name=collection_name, index_params=index_params)
        logger.info("Created HNSW index with MAX_SIM_IP on patches[embedding]")

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
        patches = [{"embedding": emb} for emb in embeddings_list]

        data = [
            {
                "doc_id": doc_id,
                "page_number": page_number,
                "patches": patches,
            }
        ]

        result = client.insert(collection_name=settings.milvus_collection_name, data=data)
        logger.info(f"Inserted page with {num_patches} patches for doc={doc_id}, page={page_number}")

        return result["insert_count"]

    def search_pages(
        self,
        query_embeddings: torch.Tensor,
        top_k: int = 10,
        doc_id_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        self._ensure_collection()
        client = self._get_client()

        if query_embeddings.dim() == 1:
            query_embeddings = query_embeddings.unsqueeze(0)

        query_list = query_embeddings.cpu().float().numpy().tolist()

        from pymilvus.client.embedding_list import EmbeddingList

        embedding_list = EmbeddingList()
        for emb in query_list:
            embedding_list.add(emb)

        search_params = {
            "metric_type": "MAX_SIM_IP",
            "params": {"ef": 64},
        }

        expr = None
        if doc_id_filter:
            expr = f'doc_id == "{doc_id_filter}"'

        results = client.search(
            collection_name=settings.milvus_collection_name,
            data=[embedding_list],
            anns_field="patches[embedding]",
            search_params=search_params,
            limit=top_k,
            filter=expr,
            output_fields=["doc_id", "page_number"],
        )

        matches = []
        for hits in results:
            for hit in hits:
                matches.append({
                    "page_id": hit["id"],
                    "doc_id": hit["entity"].get("doc_id"),
                    "page_number": hit["entity"].get("page_number"),
                    "score": hit["distance"],
                })

        logger.info(f"Search returned {len(matches)} page results")
        return matches

    def delete_document(self, doc_id: str) -> int:
        self._ensure_collection()
        client = self._get_client()

        expr = f'doc_id == "{doc_id}"'
        result = client.delete(collection_name=settings.milvus_collection_name, filter=expr)

        delete_count = result.get("delete_count", 0)
        logger.info(f"Deleted {delete_count} pages for doc={doc_id}")
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
