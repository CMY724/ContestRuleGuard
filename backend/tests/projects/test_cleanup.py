from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from contest_rule_guard.projects.cleanup import ProjectCleanupPort, ProjectCleanupRegistry

from .test_api import PAYLOAD


class RecordingCleanup(ProjectCleanupPort):
    def __init__(self) -> None:
        self.cleaned: list[UUID] = []

    def cleanup_project(self, project_id: UUID) -> None:
        self.cleaned.append(project_id)


def test_cleanup_registry_invokes_registered_derived_store_cleaners() -> None:
    first = RecordingCleanup()
    second = RecordingCleanup()
    registry = ProjectCleanupRegistry([first])
    registry.register(second)
    project_id = uuid4()

    registry.cleanup_project(project_id)

    assert first.cleaned == [project_id]
    assert second.cleaned == [project_id]


def test_delete_project_removes_each_configured_project_directory(client: TestClient) -> None:
    project_id = client.post("/api/projects", json=PAYLOAD).json()["id"]
    roots = client.app.state.settings.project_storage_roots
    for root in roots:
        project_directory = root / str(project_id)
        project_directory.mkdir(parents=True)
        (project_directory / "artifact.bin").write_bytes(b"evidence")

    response = client.delete(f"/api/projects/{project_id}")

    assert response.status_code == 204
    assert all(not (root / str(project_id)).exists() for root in roots)
