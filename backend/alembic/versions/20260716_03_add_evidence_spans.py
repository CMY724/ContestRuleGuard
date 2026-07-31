from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260716_03"
down_revision: str | None = "20260716_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "evidence_spans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("block_id", sa.Uuid(), nullable=False),
        sa.Column("field_path", sa.String(length=256), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("source_tier", sa.String(length=20), nullable=False),
        sa.Column("stage", sa.String(length=20), nullable=False),
        sa.Column("document_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"], ["normalized_documents.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_evidence_spans_document_id",
        "evidence_spans",
        ["document_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_evidence_spans_document_id", table_name="evidence_spans")
    op.drop_table("evidence_spans")
