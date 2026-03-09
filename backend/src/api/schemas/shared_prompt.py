from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.aggregates.shared_prompt import SharedPrompt
from src.domain.aggregates.prompt_favorite import PromptFavorite


class SharePromptReq(BaseModel):
    share_message: str | None = None


class SharePromptResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    prompt_id: UUID | None
    user_id: UUID
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, shared_prompt: SharedPrompt) -> SharePromptResp:
        return cls(
            id=shared_prompt.id,
            prompt_id=shared_prompt.prompt_id,
            user_id=shared_prompt.user_id,
            share_message=shared_prompt.share_message,
            like_count=shared_prompt.like_count,
            favorite_count=shared_prompt.favorite_count,
            status=shared_prompt.status,
            created_at=shared_prompt.created_at,
            updated_at=shared_prompt.updated_at,
        )


class MarketPromptResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    prompt_id: UUID | None
    user_id: UUID
    title: str  # live from Prompt
    description: str | None  # live from Prompt
    content: str  # live from Prompt
    tags: list[str]  # live from Prompt
    author_name: str  # live from User
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    is_liked: bool = False
    is_favorited: bool = False

    @classmethod
    def from_domain(
        cls,
        shared_prompt: SharedPrompt,
        title: str = "",
        description: str | None = None,
        content: str = "",
        tags: list[str] | None = None,
        author_name: str = "",
        is_liked: bool = False,
        is_favorited: bool = False,
    ) -> MarketPromptResp:
        return cls(
            id=shared_prompt.id,
            prompt_id=shared_prompt.prompt_id,
            user_id=shared_prompt.user_id,
            title=title,
            description=description,
            content=content,
            tags=tags or [],
            author_name=author_name,
            share_message=shared_prompt.share_message,
            like_count=shared_prompt.like_count,
            favorite_count=shared_prompt.favorite_count,
            status=shared_prompt.status,
            created_at=shared_prompt.created_at,
            updated_at=shared_prompt.updated_at,
            is_liked=is_liked,
            is_favorited=is_favorited,
        )


class MarketPromptListResp(BaseModel):
    items: list[MarketPromptResp]
    total: int


class PromptLikeResp(BaseModel):
    shared_prompt_id: UUID
    like_count: int
    message: str

    @classmethod
    def from_domain(cls, shared_prompt: SharedPrompt, message: str) -> PromptLikeResp:
        return cls(
            shared_prompt_id=shared_prompt.id,
            like_count=shared_prompt.like_count,
            message=message,
        )


class PromptFavoriteResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    shared_prompt_id: UUID | None
    snapshot_title: str
    snapshot_content: str
    snapshot_description: str | None
    snapshot_tags: list[str]
    snapshot_author_name: str
    snapshot_version: int
    snapshot_status: str
    created_at: datetime
    is_stale: bool = False
    like_count: int = 0
    is_liked: bool = False

    @classmethod
    def from_domain(
        cls,
        favorite: PromptFavorite,
        is_stale: bool = False,
        like_count: int = 0,
        is_liked: bool = False,
    ) -> PromptFavoriteResp:
        return cls(
            id=favorite.id,
            user_id=favorite.user_id,
            shared_prompt_id=favorite.shared_prompt_id,
            snapshot_title=favorite.snapshot_title,
            snapshot_content=favorite.snapshot_content,
            snapshot_description=favorite.snapshot_description,
            snapshot_tags=favorite.snapshot_tags,
            snapshot_author_name=favorite.snapshot_author_name,
            snapshot_version=favorite.snapshot_version,
            snapshot_status=favorite.snapshot_status,
            created_at=favorite.created_at,
            is_stale=is_stale,
            like_count=like_count,
            is_liked=is_liked,
        )


class ListPromptFavoritesResp(BaseModel):
    items: list[PromptFavoriteResp]
    total: int


class RefreshFavoriteResp(BaseModel):
    message: str
    favorite: PromptFavoriteResp
