from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "v8_skill_favorites"
down_revision: str | None = "v7_shared_skills"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "skill_favorites",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shared_skill_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("snapshot_name", sa.String(length=255), nullable=False),
        sa.Column("snapshot_description", sa.Text(), nullable=True),
        sa.Column("snapshot_slug", sa.String(length=255), nullable=False),
        sa.Column("snapshot_author_name", sa.String(length=255), nullable=False),
        sa.Column(
            "snapshot_status",
            sa.String(length=32),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skill_favorites_user_id", "skill_favorites", ["user_id"])
    op.create_index(
        "uq_skill_favorites_user_id_shared_skill_id",
        "skill_favorites",
        ["user_id", "shared_skill_id"],
        unique=True,
        postgresql_where=sa.text("shared_skill_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_skill_favorites_user_id_shared_skill_id", table_name="skill_favorites")
    op.drop_index("ix_skill_favorites_user_id", table_name="skill_favorites")
    op.drop_table("skill_favorites")
