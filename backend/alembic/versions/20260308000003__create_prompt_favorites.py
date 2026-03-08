"""create prompt_favorites table

Revision ID: v11_prompt_favorites
Revises: v10_shared_prompts
Create Date: 2026-03-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

revision = "v11_prompt_favorites"
down_revision = "v10_shared_prompts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_favorites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("shared_prompt_id", UUID(as_uuid=True), nullable=True),
        sa.Column("snapshot_title", sa.String(200), nullable=False),
        sa.Column("snapshot_content", sa.Text(), nullable=False),
        sa.Column("snapshot_description", sa.Text(), nullable=True),
        sa.Column("snapshot_tags", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("snapshot_author_name", sa.String(100), nullable=False),
        sa.Column("snapshot_version", sa.Integer(), nullable=False),
        sa.Column("snapshot_status", sa.String(30), nullable=False, server_default="active"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "user_id", "shared_prompt_id", name="uq_prompt_favorites_user_shared_prompt"
        ),
    )
    op.create_index("ix_prompt_favorites_user_id", "prompt_favorites", ["user_id"])


def downgrade() -> None:
    op.drop_table("prompt_favorites")
