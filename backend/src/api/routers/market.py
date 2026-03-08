from __future__ import annotations

from collections.abc import Awaitable, Callable
from importlib import import_module
from typing import Annotated, Literal, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.auth import get_current_user, get_optional_current_user
from src.api.dependencies.repositories import (
    SkillFavoriteRepository,
    get_shared_skill_repo,
    get_skill_favorite_repo,
    get_skill_repo,
    get_tree_repo,
)
from src.api.schemas.shared_skill import (
    FavoriteResp,
    LikeResp,
    ListFavoritesResp,
    MarketSkillListResp,
    MarketSkillResp,
)
from src.api.schemas.tree import GetTreeResp
from src.application.handlers.market_handlers import MarketSkillData, MarketSkillListData
from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill_favorite import SkillFavorite
from src.domain.aggregates.user import User
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository

MarketListHandler = Callable[
    [str | None, UUID | None, str, int, int, User | None, SharedSkillRepository, object | None],
    Awaitable[MarketSkillListData],
]
MarketDetailHandler = Callable[
    [UUID, User | None, SharedSkillRepository, object | None], Awaitable[MarketSkillData]
]
LikeHandler = Callable[[UUID, User, SharedSkillRepository], Awaitable[SharedSkill]]
FavoriteHandler = Callable[
    [UUID, User, SharedSkillRepository, object, SkillRepository], Awaitable[SkillFavorite]
]
UnfavoriteHandler = Callable[[UUID, User, SharedSkillRepository, object], Awaitable[None]]
ListFavoritesHandler = Callable[
    [User, object, int, int], Awaitable[tuple[list[SkillFavorite], int]]
]

_market_handlers = import_module("src.application.handlers.market_handlers")
_like_handlers = import_module("src.application.handlers.like_handlers")
_favorite_handlers = import_module("src.application.handlers.favorite_handlers")
_market_tree_handler = import_module("src.application.handlers.get_market_skill_tree_handler")

handle_list_market_skills = cast(MarketListHandler, _market_handlers.handle_list_market_skills)
handle_get_market_skill_detail = cast(
    MarketDetailHandler, _market_handlers.handle_get_market_skill_detail
)
handle_like_skill = cast(LikeHandler, _like_handlers.handle_like_skill)
handle_unlike_skill = cast(LikeHandler, _like_handlers.handle_unlike_skill)
handle_favorite_skill = cast(FavoriteHandler, _favorite_handlers.handle_favorite_skill)
handle_unfavorite_skill = cast(UnfavoriteHandler, _favorite_handlers.handle_unfavorite_skill)
handle_list_favorites = cast(ListFavoritesHandler, _favorite_handlers.handle_list_favorites)
handle_get_market_skill_tree = _market_tree_handler.handle_get_market_skill_tree

market_router = APIRouter(tags=["market"])


def _to_market_skill_resp(data: MarketSkillData) -> MarketSkillResp:
    return MarketSkillResp(
        id=data.id,
        skill_id=data.skill_id,
        user_id=data.user_id,
        category_id=data.category_id,
        share_message=data.share_message,
        like_count=data.like_count,
        favorite_count=data.favorite_count,
        status=data.status,
        snapshot_name=data.snapshot_name,
        snapshot_description=data.snapshot_description,
        snapshot_author_name=data.snapshot_author_name,
        is_liked=data.is_liked,
        is_favorited=data.is_favorited,
        created_at=data.created_at,
        updated_at=data.updated_at,
    )


@market_router.get("/market/skills", response_model=MarketSkillListResp)
async def list_market_skills(
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    keyword: Annotated[str | None, Query()] = None,
    category_id: Annotated[UUID | None, Query()] = None,
    sort_by: Annotated[Literal["newest", "popular"], Query()] = "newest",
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> MarketSkillListResp:
    data = await handle_list_market_skills(
        keyword,
        category_id,
        sort_by,
        skip,
        limit,
        current_user,
        shared_skill_repo,
        favorite_repo,
    )
    return MarketSkillListResp(
        items=[_to_market_skill_resp(item) for item in data.items],
        total=data.total,
    )


@market_router.get("/market/skills/{shared_skill_id}", response_model=MarketSkillResp)
async def get_market_skill_detail(
    shared_skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> MarketSkillResp:
    data = await handle_get_market_skill_detail(
        shared_skill_id,
        current_user,
        shared_skill_repo,
        favorite_repo,
    )
    return _to_market_skill_resp(data)


@market_router.post(
    "/market/skills/{shared_skill_id}/like",
    response_model=LikeResp,
    status_code=status.HTTP_201_CREATED,
)
async def like_shared_skill(
    shared_skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LikeResp:
    shared_skill = await handle_like_skill(shared_skill_id, current_user, shared_skill_repo)
    return LikeResp.from_domain(shared_skill, message="Skill liked successfully")


@market_router.delete(
    "/market/skills/{shared_skill_id}/like", response_model=LikeResp, status_code=status.HTTP_200_OK
)
async def unlike_shared_skill(
    shared_skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> LikeResp:
    shared_skill = await handle_unlike_skill(shared_skill_id, current_user, shared_skill_repo)
    return LikeResp.from_domain(shared_skill, message="Skill unliked successfully")


@market_router.post(
    "/market/skills/{shared_skill_id}/favorite",
    response_model=FavoriteResp,
    status_code=status.HTTP_201_CREATED,
)
async def favorite_skill(
    shared_skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FavoriteResp:
    favorite = await handle_favorite_skill(
        shared_skill_id,
        current_user,
        shared_skill_repo,
        favorite_repo,
        skill_repo,
    )
    return FavoriteResp.from_domain(favorite)


@market_router.delete("/market/skills/{shared_skill_id}/favorite", status_code=status.HTTP_200_OK)
async def unfavorite_skill(
    shared_skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    await handle_unfavorite_skill(shared_skill_id, current_user, shared_skill_repo, favorite_repo)
    return {"message": "ok"}


@market_router.get("/favorites", response_model=ListFavoritesResp, status_code=status.HTTP_200_OK)
async def list_favorites(
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ListFavoritesResp:
    favorites, total = await handle_list_favorites(current_user, favorite_repo, skip, limit)
    return ListFavoritesResp(
        items=[FavoriteResp.from_domain(favorite) for favorite in favorites],
        total=total,
    )


@market_router.get(
    "/market/skills/{shared_skill_id}/tree",
    response_model=GetTreeResp,
    status_code=status.HTTP_200_OK,
)
async def get_market_skill_tree(
    shared_skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    tree_repo: Annotated[TreeRepository, Depends(get_tree_repo)],
) -> GetTreeResp:
    tree = await handle_get_market_skill_tree(
        shared_skill_id=shared_skill_id,
        shared_skill_repo=shared_skill_repo,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
    )
    return GetTreeResp.from_domain(tree)


router = market_router
