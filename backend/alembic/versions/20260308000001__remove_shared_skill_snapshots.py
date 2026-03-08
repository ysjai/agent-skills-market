"""remove shared skill snapshot columns

Revision ID: v9_remove_shared_skill_snapshots
Revises: v8_skill_favorites
Create Date: 2026-03-08
"""

from alembic import op
import sqlalchemy as sa

revision = "v9_remove_shared_skill_snapshots"
down_revision = "v8_skill_favorites"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("shared_skills", "snapshot_name")
    op.drop_column("shared_skills", "snapshot_description")
    op.drop_column("shared_skills", "snapshot_author_name")


def downgrade() -> None:
    op.add_column(
        "shared_skills",
        sa.Column("snapshot_author_name", sa.String(255), nullable=False, server_default=""),
    )
    op.add_column("shared_skills", sa.Column("snapshot_description", sa.Text(), nullable=True))
    op.add_column(
        "shared_skills",
        sa.Column("snapshot_name", sa.String(255), nullable=False, server_default=""),
    )
