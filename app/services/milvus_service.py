from typing import List, Optional

import torch
from loguru import logger
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.core.config import settings


class MilvusService:
    EMBEDDING_DIM = 128
    PATCHES_PER_PAGE = 1024

    def __init__(self) -> None:
        self._collection: Optional[Collection] = None
        self._connected = False

    def connect(self) -> None:
        if self._connected:
            return

        try:
            connections.connect(
                alias="default",
                host=settings.milvus_host,
                port=settings.milvus_port,
            )
            self._connected = True
            logger.info(f"Connected to Milvus at {settings.milvus_host}:{settings.milvus_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise

    def disconnect(self) -> None:
        if not self._connected:
            return

        connections.disconnect(alias="default")
        self._connected = False
        self._collection = None
        logger.info("Disconnected from Milvus")

    def _ensure_collection(self) -> Collection:
        if self._collection is not None:
            return self._collection

        self.connect()

        if utility.has_collection(settings.milvus_collection_name):
            self._collection = Collection(settings.milvus_collection_name)
            self._collection.load()
            logger.info(f"Loaded existing collection: {settings.milvus_collection_name}")
            return self._collection

        return self._create_collection()

    def _create_collection(self) -> Collection:
        fields = [
            FieldSchema(
                name="patch_id",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="doc_id",
                dtype=DataType.VARCHAR,
                max_length=64,
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.INT32,
            ),
            FieldSchema(
                name="patch_index",
                dtype=DataType.INT32,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.EMBEDDING_DIM,
            ),
        ]

        schema = CollectionSchema(fields=fields, enable_dynamic_field=False)
        self._collection = Collection(name=settings.milvus_collection_name, schema=schema)
        logger.info(f"Created collection: {settings.milvus_collection_name}")

        self._create_indexes()
        self._collection.load()

        return self._collection

    def _create_indexes(self) -> None:
        if self._collection is None:
            raise RuntimeError("Collection not initialized")

        hnsw_params = {
            "metric_type": "IP",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 256},
        }
        self._collection.create_index(field_name="embedding", index_params=hnsw_params)
        logger.info("Created HNSW index on embedding field")

        trie_params = {
            "index_type": "Trie",
        }
        self._collection.create_index(field_name="doc_id", index_params=trie_params)
        logger.info("Created Trie index on doc_id field")

    def insert_page_embeddings(
        self,
        doc_id: str,
        page_number: int,
        embeddings: torch.Tensor,
    ) -> List[int]:
        collection = self._ensure_collection()

        if embeddings.dim() != 2:
            raise ValueError(f"Expected 2D tensor, got {embeddings.dim()}D")

        num_patches = embeddings.shape[0]
        embedding_dim = embeddings.shape[1]

        if embedding_dim != self.EMBEDDING_DIM:
            raise ValueError(f"Expected embedding dim {self.EMBEDDING_DIM}, got {embedding_dim}")

        embeddings_list = embeddings.cpu().float().numpy().tolist()

        data = [
            [doc_id] * num_patches,
            [page_number] * num_patches,
            list(range(num_patches)),
            embeddings_list,
        ]

        result = collection.insert(data)
        collection.flush()

        logger.info(f"Inserted {num_patches} patches for doc={doc_id}, page={page_number}")
        return result.primary_keys

    def search_patches(
        self,
        query_embedding: torch.Tensor,
        top_k: int = 10,
        doc_id_filter: Optional[str] = None,
    ) -> List[dict]:
        collection = self._ensure_collection()

        if query_embedding.dim() == 1:
            query_embedding = query_embedding.unsqueeze(0)

        query_vectors = query_embedding.cpu().float().numpy().tolist()

        search_params = {
            "metric_type": "IP",
            "params": {"ef": 64},
        }

        expr = None
        if doc_id_filter:
            expr = f'doc_id == "{doc_id_filter}"'

        results = collection.search(
            data=query_vectors,
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["doc_id", "page_number", "patch_index"],
        )

        matches = []
        for hits in results:
            for hit in hits:
                matches.append({
                    "patch_id": hit.id,
                    "doc_id": hit.entity.get("doc_id"),
                    "page_number": hit.entity.get("page_number"),
                    "patch_index": hit.entity.get("patch_index"),
                    "score": hit.score,
                })

        logger.info(f"Search returned {len(matches)} results")
        return matches

    def get_page_embeddings(self, doc_id: str, page_number: int) -> List[dict]:
        collection = self._ensure_collection()

        expr = f'doc_id == "{doc_id}" and page_number == {page_number}'

        results = collection.query(
            expr=expr,
            output_fields=["patch_id", "doc_id", "page_number", "patch_index", "embedding"],
        )

        logger.info(f"Retrieved {len(results)} patches for doc={doc_id}, page={page_number}")
        return results

    def delete_document(self, doc_id: str) -> int:
        collection = self._ensure_collection()

        expr = f'doc_id == "{doc_id}"'

        result = collection.delete(expr)
        collection.flush()

        delete_count = result.delete_count
        logger.info(f"Deleted {delete_count} patches for doc={doc_id}")
        return delete_count


_milvus_service: Optional[MilvusService] = None


def get_milvus_service() -> MilvusService:
    global _milvus_service
    if _milvus_service is None:
        _milvus_service = MilvusService()
    return _milvus_service
