from pathlib import Path

from sqlalchemy import create_engine, inspect

from alembic import command
from alembic.config import Config

BACKEND = Path(__file__).parents[2]


def test_upgrade_head_twice_creates_project_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "migration.db"
    config = Config(BACKEND / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    config.set_main_option("prepend_sys_path", str(BACKEND / "src"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")

    command.upgrade(config, "head")
    command.upgrade(config, "head")

    inspector = inspect(create_engine(f"sqlite:///{database_path.as_posix()}"))
    tables = set(inspector.get_table_names())
    assert {"alembic_version", "projects", "model_usage_events"}.issubset(tables)
    assert {column["name"] for column in inspector.get_columns("projects")} == {
        "id",
        "name",
        "competition_name",
        "competition_year",
        "track",
        "target_stage",
        "created_at",
        "updated_at",
    }
    assert {
        column["name"] for column in inspector.get_columns("model_usage_events")
    } == {
        "id",
        "project_id",
        "purpose",
        "status",
        "reserved_cost_yuan",
        "charged_cost_yuan",
        "prompt_tokens",
        "completion_tokens",
        "created_at",
        "finalized_at",
    }
    indexes = {
        index["name"]: tuple(index["column_names"])
        for index in inspector.get_indexes("model_usage_events")
    }
    assert indexes == {
        "ix_model_usage_events_project_id": ("project_id",),
        "ix_model_usage_events_purpose": ("purpose",),
        "ix_model_usage_events_status": ("status",),
    }
    foreign_keys = inspector.get_foreign_keys("model_usage_events")
    assert len(foreign_keys) == 1
    assert foreign_keys[0]["referred_table"] == "projects"
    assert foreign_keys[0]["constrained_columns"] == ["project_id"]
    assert foreign_keys[0]["options"]["ondelete"] == "CASCADE"
