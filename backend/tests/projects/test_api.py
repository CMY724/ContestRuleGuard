from uuid import UUID

from fastapi.testclient import TestClient

PAYLOAD = {
    "name": "赛规通",
    "competition_name": "全球校园人工智能算法精英大赛",
    "competition_year": 2026,
    "track": "算法创新赛",
    "target_stage": "school",
}


def test_create_and_list_projects_use_snake_case(client: TestClient) -> None:
    created = client.post("/api/projects", json=PAYLOAD)
    assert created.status_code == 201
    body = created.json()
    assert str(UUID(body["id"])) == body["id"]
    assert body | PAYLOAD == body
    assert set(body) == {
        "id",
        "name",
        "competition_name",
        "competition_year",
        "track",
        "target_stage",
        "created_at",
        "updated_at",
    }

    listed = client.get("/api/projects")
    assert listed.status_code == 200
    assert listed.json() == [body]


def test_get_and_patch_project(client: TestClient) -> None:
    project_id = client.post("/api/projects", json=PAYLOAD).json()["id"]
    updated = client.patch(
        f"/api/projects/{project_id}",
        json={"name": "赛规通国赛版", "target_stage": "national"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "赛规通国赛版"
    assert updated.json()["target_stage"] == "national"
    assert client.get(f"/api/projects/{project_id}").json() == updated.json()


def test_delete_project_and_return_404(client: TestClient) -> None:
    project_id = client.post("/api/projects", json=PAYLOAD).json()["id"]
    assert client.delete(f"/api/projects/{project_id}").status_code == 204
    missing = client.get(f"/api/projects/{project_id}")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "project not found"}


def test_invalid_project_uuid_is_rejected_at_api_boundary(client: TestClient) -> None:
    assert client.get("/api/projects/not-a-uuid").status_code == 422


def test_project_timestamps_are_serialized_as_explicit_utc(client: TestClient) -> None:
    body = client.post("/api/projects", json=PAYLOAD).json()

    assert body["created_at"].endswith("Z")
    assert body["updated_at"].endswith("Z")
