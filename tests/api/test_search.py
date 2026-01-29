import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.integration
def test_search_vidore_first_page_score(client):
    response = client.post(
        "/api/search",
        json={"query": "ViDoRe", "top_k": 5},
    )

    assert response.status_code == 200

    data = response.json()
    first_result = data["results"][0]

    assert first_result["page_number"] == 1
    assert first_result["score"] > 0

    print(f"\nViDoRe search - Page 1 MaxSim score: {first_result['score']:.2f}")
