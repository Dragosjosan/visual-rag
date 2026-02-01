from pymilvus import MilvusClient
import numpy as np

from src.core.config import settings


def check_embeddings():
    client = MilvusClient(uri=f"http://{settings.milvus_host}:{settings.milvus_port}")
    collection_name = settings.milvus_collection_name

    if not client.has_collection(collection_name):
        print(f"Collection {collection_name} does not exist")
        return

    results = client.query(
        collection_name=collection_name,
        filter="",
        output_fields=["doc_id", "page_number", "patch_index", "embedding"],
        limit=200,
    )

    print(f"Total patches retrieved: {len(results)}")

    docs = {}
    for r in results:
        doc_id = r["doc_id"]
        if doc_id not in docs:
            docs[doc_id] = {}
        page = r["page_number"]
        patch_idx = r["patch_index"]
        if page not in docs[doc_id]:
            docs[doc_id][page] = {}
        docs[doc_id][page][patch_idx] = np.array(r["embedding"])

    for doc_id, pages in docs.items():
        print(f"\nDocument: {doc_id[:16]}...")
        print(f"  Pages: {len(pages)}")

        page_nums = sorted(pages.keys())
        if len(page_nums) < 2:
            continue

        print("\n  Patch 0 (CLS token - should be identical):")
        for i in range(min(3, len(page_nums) - 1)):
            p1, p2 = page_nums[i], page_nums[i + 1]
            if 0 in pages[p1] and 0 in pages[p2]:
                diff = np.linalg.norm(pages[p1][0] - pages[p2][0])
                print(f"    Page {p1} vs {p2}: diff = {diff:.6f}")

        print("\n  Patch 10 (image content - should differ):")
        for i in range(min(3, len(page_nums) - 1)):
            p1, p2 = page_nums[i], page_nums[i + 1]
            if 10 in pages[p1] and 10 in pages[p2]:
                diff = np.linalg.norm(pages[p1][10] - pages[p2][10])
                status = "OK" if diff > 0.1 else "WARNING: too similar"
                print(f"    Page {p1} vs {p2}: diff = {diff:.6f} [{status}]")


if __name__ == "__main__":
    check_embeddings()
