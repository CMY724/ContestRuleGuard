from fastapi.testclient import TestClient

from contest_rule_guard.core.config import Settings
from contest_rule_guard.main import create_app


def test_health_returns_service_identity() -> None:
    app = create_app(
        Settings(
            app_name="赛规通测试 API",
            environment="test",
            database_url="sqlite:///:memory:",
            frontend_origin="http://localhost:5173",
        )
    )
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "赛规通测试 API",
        "environment": "test",
    }
