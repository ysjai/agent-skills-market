from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "v6_categories"
down_revision: str | None = "v5_prompts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
        sa.UniqueConstraint("slug"),
    )

    # Seed data with 9 categories
    categories = [
        {
            "name": "Coding",
            "slug": "coding",
            "description": "Programming and code-related skills",
            "display_order": 1,
            "is_active": True,
        },
        {
            "name": "DevOps",
            "slug": "devops",
            "description": "DevOps and infrastructure skills",
            "display_order": 2,
            "is_active": True,
        },
        {
            "name": "Testing",
            "slug": "testing",
            "description": "Testing and quality assurance skills",
            "display_order": 3,
            "is_active": True,
        },
        {
            "name": "Documentation",
            "slug": "documentation",
            "description": "Documentation and technical writing skills",
            "display_order": 4,
            "is_active": True,
        },
        {
            "name": "Automation",
            "slug": "automation",
            "description": "Automation and workflow skills",
            "display_order": 5,
            "is_active": True,
        },
        {
            "name": "Security",
            "slug": "security",
            "description": "Security and compliance skills",
            "display_order": 6,
            "is_active": True,
        },
        {
            "name": "Data",
            "slug": "data",
            "description": "Data processing and analytics skills",
            "display_order": 7,
            "is_active": True,
        },
        {
            "name": "AI/ML",
            "slug": "ai-ml",
            "description": "Artificial intelligence and machine learning skills",
            "display_order": 8,
            "is_active": True,
        },
        {
            "name": "Other",
            "slug": "other",
            "description": "Other uncategorized skills",
            "display_order": 9,
            "is_active": True,
        },
    ]

    op.execute(
        sa.insert(
            sa.table(
                "categories",
                sa.column("name"),
                sa.column("slug"),
                sa.column("description"),
                sa.column("display_order"),
                sa.column("is_active"),
            )
        ).values(categories)
    )


def downgrade() -> None:
    op.drop_table("categories")
