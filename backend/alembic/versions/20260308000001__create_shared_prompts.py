"""create shared_prompts and prompt_likes tables

Revision ID: v9_shared_prompts
Revises: v8_skill_favorites
Create Date: 2026-03-08
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "v9_shared_prompts"
down_revision = "v8_skill_favorites"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shared_prompts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "prompt_id",
            UUID(as_uuid=True),
            sa.ForeignKey("prompts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("share_message", sa.Text(), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("favorite_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_shared_prompts_status", "shared_prompts", ["status"])
    op.create_index("ix_shared_prompts_user_id", "shared_prompts", ["user_id"])

    op.create_table(
        "prompt_likes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "shared_prompt_id",
            UUID(as_uuid=True),
            sa.ForeignKey("shared_prompts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "user_id", "shared_prompt_id", name="uq_prompt_likes_user_shared_prompt"
        ),
    )


def downgrade() -> None:
    op.drop_table("prompt_likes")
    op.drop_table("shared_prompts")
