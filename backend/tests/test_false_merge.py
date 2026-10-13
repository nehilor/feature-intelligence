from fastapi.testclient import TestClient


def test_no_merge_endpoint(client: TestClient) -> None:
    response = client.post("/api/feature-requests/any-id/merge", json={})
    assert response.status_code == 404


def test_duplicate_classification_does_not_delete_requests(client: TestClient) -> None:
    create_a = client.post(
        "/api/feature-requests",
        json={"title": "Export reports to CSV", "description": "Need CSV export for finance reporting."},
    )
    create_b = client.post(
        "/api/feature-requests",
        json={"title": "Download dashboard data", "description": "Need spreadsheet export for analytics."},
    )
    a_id = create_a.json()["id"]
    b_id = create_b.json()["id"]
    before = client.get(f"/api/feature-requests/{a_id}").json()
    client.post(f"/api/feature-requests/{a_id}/relationships/analyze")
    after = client.get(f"/api/feature-requests/{a_id}").json()
    assert after["title"] == before["title"]
    assert after["description"] == before["description"]
    still_b = client.get(f"/api/feature-requests/{b_id}")
    assert still_b.status_code == 200
