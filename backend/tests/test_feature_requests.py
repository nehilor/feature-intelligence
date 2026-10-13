import pytest


def _create(client, title="Valid title here", description="Valid description with enough length."):
    return client.post(
        "/api/feature-requests",
        json={"title": title, "description": description},
    )


class TestCreate:
    def test_valid_request_returns_201(self, client):
        response = _create(client)
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "SUBMITTED"
        assert body["support_count"] == 0
        assert body["title"] == "Valid title here"

    def test_trims_title_and_description(self, client):
        response = client.post(
            "/api/feature-requests",
            json={"title": "  Trim me  ", "description": "  Trim description value here.  "},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Trim me"
        assert body["description"] == "Trim description value here."

    @pytest.mark.parametrize(
        "title",
        ["ab", "   ", "x" * 121],
    )
    def test_invalid_title_rejected(self, client, title):
        response = _create(client, title=title)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "description",
        ["short", "   ", "x" * 4001],
    )
    def test_invalid_description_rejected(self, client, description):
        response = _create(client, description=description)
        assert response.status_code == 422


class TestList:
    def test_empty_list(self, client):
        response = client.get("/api/feature-requests")
        assert response.status_code == 200
        body = response.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_multiple_requests(self, client):
        _create(client, title="First request title", description="First request description text.")
        _create(client, title="Second request title", description="Second request description text.")
        response = client.get("/api/feature-requests")
        assert response.json()["total"] == 2

    def test_recent_sort(self, client):
        first = _create(client, title="Older request title", description="Older request description here.")
        second = _create(client, title="Newer request title", description="Newer request description here.")
        response = client.get("/api/feature-requests?sort=recent")
        ids = [item["id"] for item in response.json()["items"]]
        assert ids.index(second.json()["id"]) < ids.index(first.json()["id"])

    def test_supported_sort(self, client):
        low = _create(client, title="Low support title", description="Low support description here.")
        high = _create(client, title="High support title", description="High support description here.")
        client.post(f"/api/feature-requests/{high.json()['id']}/support", json={"supporter_key": "a"})
        client.post(f"/api/feature-requests/{high.json()['id']}/support", json={"supporter_key": "b"})
        client.post(f"/api/feature-requests/{low.json()['id']}/support", json={"supporter_key": "c"})
        response = client.get("/api/feature-requests?sort=supported")
        assert response.json()["items"][0]["id"] == high.json()["id"]

    def test_text_search(self, client):
        _create(client, title="Export reports to CSV", description="Finance export workflow.")
        _create(client, title="Dark mode", description="Night theme preference.")
        response = client.get("/api/feature-requests?q=export")
        assert response.json()["total"] == 1
        assert "Export" in response.json()["items"][0]["title"]

    def test_pagination(self, client):
        for index in range(3):
            _create(client, title=f"Paginate title {index}", description=f"Paginate description {index} here.")
        page = client.get("/api/feature-requests?limit=2&offset=0").json()
        assert len(page["items"]) == 2
        assert page["total"] == 3

    def test_invalid_pagination(self, client):
        assert client.get("/api/feature-requests?limit=0").status_code == 422
        assert client.get("/api/feature-requests?limit=1000").status_code == 422
        assert client.get("/api/feature-requests?offset=-1").status_code == 422


class TestDetail:
    def test_known_request(self, client):
        created = _create(client).json()
        response = client.get(f"/api/feature-requests/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_unknown_request_404(self, client):
        response = client.get("/api/feature-requests/not-a-real-id")
        assert response.status_code == 404


class TestSupport:
    def test_new_support(self, client):
        created = _create(client).json()
        response = client.post(
            f"/api/feature-requests/{created['id']}/support",
            json={"supporter_key": "browser-1"},
        )
        body = response.json()
        assert body["new_support"] is True
        assert body["support_count"] == 1

    def test_repeated_support_idempotent(self, client):
        created = _create(client).json()
        url = f"/api/feature-requests/{created['id']}/support"
        first = client.post(url, json={"supporter_key": "browser-1"}).json()
        second = client.post(url, json={"supporter_key": "browser-1"}).json()
        assert first["support_count"] == 1
        assert second["new_support"] is False
        assert second["support_count"] == 1

    def test_different_supporter_increments(self, client):
        created = _create(client).json()
        url = f"/api/feature-requests/{created['id']}/support"
        client.post(url, json={"supporter_key": "browser-1"})
        second = client.post(url, json={"supporter_key": "browser-2"}).json()
        assert second["support_count"] == 2

    def test_support_unknown_request_404(self, client):
        response = client.post(
            "/api/feature-requests/missing-id/support",
            json={"supporter_key": "browser-1"},
        )
        assert response.status_code == 404

    def test_invalid_supporter_key(self, client):
        created = _create(client).json()
        response = client.post(
            f"/api/feature-requests/{created['id']}/support",
            json={"supporter_key": "   "},
        )
        assert response.status_code == 422


class TestCurrentSupporterState:
    def test_supported_by_current_user_on_detail(self, client):
        created = _create(client).json()
        client.post(
            f"/api/feature-requests/{created['id']}/support",
            json={"supporter_key": "browser-abc"},
        )
        detail = client.get(
            f"/api/feature-requests/{created['id']}?supporter_key=browser-abc",
        ).json()
        assert detail["supported_by_current_user"] is True

        other = client.get(
            f"/api/feature-requests/{created['id']}?supporter_key=other-browser",
        ).json()
        assert other["supported_by_current_user"] is False
