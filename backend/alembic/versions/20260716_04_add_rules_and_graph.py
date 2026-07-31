from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260716_04"
down_revision: str | None = "20260716_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contest_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("rule_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("scope_json", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("bindings_json", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contest_rules_project_id", "contest_rules", ["project_id"])
    op.create_index("ix_contest_rules_rule_type", "contest_rules", ["rule_type"])
    op.create_index("ix_contest_rules_status", "contest_rules", ["status"])

    op.create_table(
        "graph_nodes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("ref_id", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "graph_edges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("relation", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_graph_edges_source_id", "graph_edges", ["source_id"])
    op.create_index("ix_graph_edges_target_id", "graph_edges", ["target_id"])


def downgrade() -> None:
    op.drop_index("ix_graph_edges_target_id", table_name="graph_edges")
    op.drop_index("ix_graph_edges_source_id", table_name="graph_edges")
    op.drop_table("graph_edges")
    op.drop_table("graph_nodes")
    op.drop_index("ix_contest_rules_status", table_name="contest_rules")
    op.drop_index("ix_contest_rules_rule_type", table_name="contest_rules")
    op.drop_index("ix_contest_rules_project_id", table_name="contest_rules")
    op.drop_table("contest_rules")
