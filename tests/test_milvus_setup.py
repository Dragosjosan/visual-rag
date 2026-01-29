from loguru import logger

from app.core.milvus_client import milvus_client


def test_milvus_connection_and_collection():
    logger.info("Testing Milvus connection and collection setup")

    milvus_client.connect()

    collection = milvus_client.create_collection(dimension=128)
    assert collection is not None
    assert collection.name == "visual_rag_patches"

    schema = collection.schema
    field_names = [field.name for field in schema.fields]
    assert "patch_id" in field_names
    assert "doc_id" in field_names
    assert "page_number" in field_names
    assert "patch_index" in field_names
    assert "embedding" in field_names

    retrieved = milvus_client.get_collection()
    assert retrieved is not None
    assert retrieved.name == collection.name

    milvus_client.disconnect()
    logger.success("Milvus connection and collection test passed")


if __name__ == "__main__":
    test_milvus_connection_and_collection()
