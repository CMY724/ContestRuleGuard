from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from contest_rule_guard.core.config import Settings
from contest_rule_guard.db.base import Base
from contest_rule_guard.main import create_app


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    database_url = f"sqlite:///{(tmp_path / 'api.db').as_posix()}"
    app = create_app(
        Settings(
            environment="test",
            database_url=database_url,
            project_storage_roots=(
                tmp_path / "uploads",
                tmp_path / "submission-artifacts",
                tmp_path / "reports",
            ),
        )
    )
    Base.metadata.create_all(app.state.engine)
    with TestClient(app) as test_client:
        yield test_client
