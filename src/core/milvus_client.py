from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from src.core.config import settings


class MilvusClient:
    def __init__(self):
        self.collection_name = settings.milvus_collection_name
        self.collection: Collection | None = None

    def connect(self) -> None:
        connections.connect(
            alias="default",
            host=settings.milvus_host,
            port=settings.milvus_port,
        )

    def disconnect(self) -> None:
        connections.disconnect(alias="default")

    def create_collection(self, dimension: int = 128) -> Collection:
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            return self.collection

        fields = [
            FieldSchema(name="patch_id", dtype=DataType.VARCHAR, is_primary=True, max_length=256),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="page_number", dtype=DataType.INT32),
            FieldSchema(name="patch_index", dtype=DataType.INT32),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        ]

        schema = CollectionSchema(fields=fields)
        self.collection = Collection(name=self.collection_name, schema=schema)

        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)

        return self.collection

    def get_collection(self) -> Collection | None:
        if self.collection:
            return self.collection

        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            return self.collection

        return None


milvus_client = MilvusClient()
