from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260716_02"
down_revision: str | None = "20260716_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "normalized_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column("media_type", sa.String(length=128), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("source_tier", sa.String(length=20), nullable=False),
        sa.Column("stage", sa.String(length=20), nullable=False),
        sa.Column("units_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_normalized_documents_project_id",
        "normalized_documents",
        ["project_id"],
    )
    op.create_index(
        "ix_normalized_documents_content_sha256",
        "normalized_documents",
        ["content_sha256"],
    )


def downgrade() -> None:
    op.drop_index("ix_normalized_documents_content_sha256", table_name="normalized_documents")
    op.drop_index("ix_normalized_documents_project_id", table_name="normalized_documents")
    op.drop_table("normalized_documents")
