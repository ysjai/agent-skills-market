from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.aggregates.category import Category


class CategoryResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, category: Category) -> CategoryResp:
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug.value,
            description=category.description,
            display_order=category.display_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )


class ListCategoriesResp(BaseModel):
    items: list[CategoryResp]
    total: int
