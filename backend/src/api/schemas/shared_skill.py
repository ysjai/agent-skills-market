from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.api.schemas.category import CategoryResp
from src.domain.aggregates.category import Category
from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill_favorite import SkillFavorite


class ShareSkillReq(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(str_strip_whitespace=True)

    category_id: UUID
    share_message: str | None = Field(default=None, max_length=2000)


class ShareSkillResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    skill_id: UUID | None
    category_id: UUID
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    snapshot_name: str
    snapshot_description: str | None
    snapshot_author_name: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, shared_skill: SharedSkill) -> ShareSkillResp:
        return cls(
            id=shared_skill.id,
            skill_id=shared_skill.skill_id,
            category_id=shared_skill.category_id,
            share_message=shared_skill.share_message,
            like_count=shared_skill.like_count,
            favorite_count=shared_skill.favorite_count,
            status=shared_skill.status,
            snapshot_name=shared_skill.snapshot_name,
            snapshot_description=shared_skill.snapshot_description,
            snapshot_author_name=shared_skill.snapshot_author_name,
            created_at=shared_skill.created_at,
            updated_at=shared_skill.updated_at,
        )


class SharedSkillDetailResp(ShareSkillResp):
    category: CategoryResp

    @classmethod
    def from_shared_skill(
        cls,
        shared_skill: SharedSkill,
        category: Category,
    ) -> SharedSkillDetailResp:
        base = ShareSkillResp.from_domain(shared_skill)
        return cls(
            id=base.id,
            skill_id=base.skill_id,
            category_id=base.category_id,
            share_message=base.share_message,
            like_count=base.like_count,
            favorite_count=base.favorite_count,
            status=base.status,
            snapshot_name=base.snapshot_name,
            snapshot_description=base.snapshot_description,
            snapshot_author_name=base.snapshot_author_name,
            created_at=base.created_at,
            updated_at=base.updated_at,
            category=CategoryResp.from_domain(category),
        )


class MarketSkillResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    skill_id: UUID | None
    user_id: UUID
    category_id: UUID
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    snapshot_name: str
    snapshot_description: str | None
    snapshot_author_name: str
    is_liked: bool = False
    is_favorited: bool = False
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(
        cls,
        shared_skill: SharedSkill,
        is_liked: bool = False,
        is_favorited: bool = False,
    ) -> MarketSkillResp:
        return cls(
            id=shared_skill.id,
            skill_id=shared_skill.skill_id,
            user_id=shared_skill.user_id,
            category_id=shared_skill.category_id,
            share_message=shared_skill.share_message,
            like_count=shared_skill.like_count,
            favorite_count=shared_skill.favorite_count,
            status=shared_skill.status,
            snapshot_name=shared_skill.snapshot_name,
            snapshot_description=shared_skill.snapshot_description,
            snapshot_author_name=shared_skill.snapshot_author_name,
            is_liked=is_liked,
            is_favorited=is_favorited,
            created_at=shared_skill.created_at,
            updated_at=shared_skill.updated_at,
        )


class MarketSkillListResp(BaseModel):
    items: list[MarketSkillResp]
    total: int


class LikeResp(BaseModel):
    shared_skill_id: UUID
    like_count: int
    message: str

    @classmethod
    def from_domain(cls, shared_skill: SharedSkill, message: str) -> LikeResp:
        return cls(
            shared_skill_id=shared_skill.id,
            like_count=shared_skill.like_count,
            message=message,
        )


class FavoriteResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    shared_skill_id: UUID | None
    snapshot_name: str
    snapshot_description: str | None
    snapshot_slug: str
    snapshot_author_name: str
    snapshot_status: str
    created_at: datetime

    @classmethod
    def from_domain(cls, favorite: SkillFavorite) -> FavoriteResp:
        return cls(
            id=favorite.id,
            user_id=favorite.user_id,
            shared_skill_id=favorite.shared_skill_id,
            snapshot_name=favorite.snapshot_name,
            snapshot_description=favorite.snapshot_description,
            snapshot_slug=favorite.snapshot_slug,
            snapshot_author_name=favorite.snapshot_author_name,
            snapshot_status=favorite.snapshot_status,
            created_at=favorite.created_at,
        )


class ListFavoritesResp(BaseModel):
    items: list[FavoriteResp]
    total: int
