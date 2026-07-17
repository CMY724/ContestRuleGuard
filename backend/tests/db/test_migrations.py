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
    assert {"alembic_version", "projects"}.issubset(tables)
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
