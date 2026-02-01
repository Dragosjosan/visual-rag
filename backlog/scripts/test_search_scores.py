from src.services.retrieval_service import get_retrieval_service


def test_search_scores():
    service = get_retrieval_service()

    queries = ["author", "introduction", "conclusion", "table", "figure"]

    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)

        try:
            results = service.retrieve(query, top_k=10)
        except Exception as e:
            print(f"  Error: {e}")
            continue

        if not results:
            print("  No results found")
            continue

        scores = [r.score for r in results]
        unique_scores = len(set(f"{s:.4f}" for s in scores))

        for r in results[:5]:
            print(f"  Page {r.page_number:2d}: score = {r.score:.4f}")

        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more")

        print(f"\n  Score range: {min(scores):.4f} to {max(scores):.4f}")
        print(f"  Unique scores: {unique_scores} of {len(scores)}")

        if unique_scores == 1:
            print("  WARNING: All scores identical - MaxSim bug may be present!")
        elif unique_scores < len(scores) // 2:
            print("  INFO: Many duplicate scores - may indicate similar pages")
        else:
            print("  OK: Scores vary as expected")


if __name__ == "__main__":
    test_search_scores()
