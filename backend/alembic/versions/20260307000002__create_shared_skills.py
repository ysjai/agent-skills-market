from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "v7_shared_skills"
down_revision: str | None = "v6_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shared_skills",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("share_message", sa.Text(), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("favorite_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("snapshot_name", sa.String(length=255), nullable=False),
        sa.Column("snapshot_description", sa.Text(), nullable=True),
        sa.Column("snapshot_author_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shared_skills_user_id", "shared_skills", ["user_id"])
    op.create_index("ix_shared_skills_status", "shared_skills", ["status"])
    op.create_index("ix_shared_skills_category_id", "shared_skills", ["category_id"])

    op.create_table(
        "skill_likes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shared_skill_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "shared_skill_id", name="uq_skill_likes_user_id_shared_skill_id"
        ),
    )
    op.create_index("ix_skill_likes_user_id", "skill_likes", ["user_id"])
    op.create_index("ix_skill_likes_shared_skill_id", "skill_likes", ["shared_skill_id"])


def downgrade() -> None:
    op.drop_index("ix_skill_likes_shared_skill_id", table_name="skill_likes")
    op.drop_index("ix_skill_likes_user_id", table_name="skill_likes")
    op.drop_table("skill_likes")
    op.drop_index("ix_shared_skills_category_id", table_name="shared_skills")
    op.drop_index("ix_shared_skills_status", table_name="shared_skills")
    op.drop_index("ix_shared_skills_user_id", table_name="shared_skills")
    op.drop_table("shared_skills")
