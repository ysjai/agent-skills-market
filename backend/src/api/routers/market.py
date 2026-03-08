from __future__ import annotations

from collections.abc import Awaitable, Callable
from importlib import import_module
from typing import Annotated, Literal, cast
from uuid import UUID

import yaml
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from src.api.dependencies.auth import get_current_user, get_optional_current_user
from src.api.dependencies.repositories import (
    SkillFavoriteRepository,
    get_blob_repo,
    get_prompt_favorite_repo,
    get_prompt_repo,
    get_shared_prompt_repo,
    get_shared_skill_repo,
    get_skill_favorite_repo,
    get_skill_repo,
    get_tree_repo,
    get_user_repo,
)
from src.api.schemas.shared_prompt import (
    ListPromptFavoritesResp,
    MarketPromptListResp,
    MarketPromptResp,
    PromptFavoriteResp,
    PromptLikeResp,
    RefreshFavoriteResp,
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
from src.application.handlers.prompt_favorite_handlers import (
    handle_check_favorite_version,
    handle_favorite_prompt,
    handle_list_prompt_favorites,
    handle_refresh_favorite,
    handle_unfavorite_prompt,
)
from src.application.handlers.prompt_like_handlers import handle_like_prompt, handle_unlike_prompt
from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill_favorite import SkillFavorite
from src.domain.aggregates.user import User
from src.domain.repositories.prompt_favorite_repository import PromptFavoriteRepository
from src.domain.repositories.prompt_repository import PromptRepository
from src.domain.repositories.shared_prompt_repository import SharedPromptRepository
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.user_repository import UserRepository

MarketListHandler = Callable[
    [
        str | None,
        UUID | None,
        str,
        int,
        int,
        User | None,
        SharedSkillRepository,
        object | None,
        SkillRepository | None,
        UserRepository | None,
    ],
    Awaitable[MarketSkillListData],
]
MarketDetailHandler = Callable[
    [
        UUID,
        User | None,
        SharedSkillRepository,
        object | None,
        SkillRepository | None,
        UserRepository | None,
    ],
    Awaitable[MarketSkillData],
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
_market_blob_handler = import_module("src.application.handlers.get_market_blob_handler")

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
handle_get_market_blob = _market_blob_handler.handle_get_market_blob

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
        name=data.name,
        description=data.description,
        author_name=data.author_name,
        is_liked=data.is_liked,
        is_favorited=data.is_favorited,
        created_at=data.created_at,
        updated_at=data.updated_at,
    )


@market_router.get("/market/skills", response_model=MarketSkillListResp)
async def list_market_skills(
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
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
        skill_repo,
        user_repo,
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
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> MarketSkillResp:
    data = await handle_get_market_skill_detail(
        shared_skill_id,
        current_user,
        shared_skill_repo,
        favorite_repo,
        skill_repo,
        user_repo,
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


@market_router.get(
    "/favorites/skills", response_model=ListFavoritesResp, status_code=status.HTTP_200_OK
)
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


@market_router.get("/market/skills/{shared_skill_id}/blobs/{blob_id}")
async def get_market_skill_blob(
    shared_skill_id: UUID,
    blob_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    tree_repo: Annotated[TreeRepository, Depends(get_tree_repo)],
    blob_repo: Annotated[BlobRepository, Depends(get_blob_repo)],
    content_type: str | None = None,
) -> Response:
    blob = await handle_get_market_blob(
        shared_skill_id=shared_skill_id,
        blob_id=blob_id,
        shared_skill_repo=shared_skill_repo,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
    )
    media_type = content_type or "application/octet-stream"
    return Response(
        content=blob.get_raw_content(),
        media_type=media_type,
    )


# ---------------------------------------------------------------------------
# Prompt market endpoints
# ---------------------------------------------------------------------------


@market_router.get("/market/prompts", response_model=MarketPromptListResp)
async def list_market_prompts(
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    prompt_favorite_repo: Annotated[PromptFavoriteRepository, Depends(get_prompt_favorite_repo)],
    prompt_repo: Annotated[PromptRepository, Depends(get_prompt_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
    keyword: Annotated[str | None, Query()] = None,
    tags: Annotated[list[str], Query()] = [],  # noqa: B006
    sort_by: Annotated[Literal["newest", "popular"], Query()] = "newest",
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> MarketPromptListResp:
    shared_prompts = await shared_prompt_repo.find_active_by_filters(
        keyword=keyword, tags=tags, sort_by=sort_by, skip=skip, limit=limit
    )
    total = await shared_prompt_repo.count_active_by_filters(keyword=keyword, tags=tags)

    items: list[MarketPromptResp] = []
    for sp in shared_prompts:
        title, description, content, tags_data = "", None, "", []
        author_name = ""

        if sp.prompt_id:
            prompt = await prompt_repo.get_by_id(sp.prompt_id)
            if prompt:
                title = prompt.title
                description = prompt.description
                content = prompt.content
                tags_data = list(prompt.tags)

        user = await user_repo.get_by_id(sp.user_id)
        if user:
            author_name = user.username

        is_liked = False
        is_favorited = False
        if current_user:
            like = await shared_prompt_repo.find_like(current_user.id, sp.id)
            is_liked = like is not None
            fav = await prompt_favorite_repo.find_by_user_and_shared_prompt(current_user.id, sp.id)
            is_favorited = fav is not None

        items.append(
            MarketPromptResp.from_domain(
                sp,
                title=title,
                description=description,
                content=content,
                tags=tags_data,
                author_name=author_name,
                is_liked=is_liked,
                is_favorited=is_favorited,
            )
        )

    return MarketPromptListResp(items=items, total=total)


@market_router.get("/market/prompts/{shared_prompt_id}", response_model=MarketPromptResp)
async def get_market_prompt_detail(
    shared_prompt_id: UUID,
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    prompt_favorite_repo: Annotated[PromptFavoriteRepository, Depends(get_prompt_favorite_repo)],
    prompt_repo: Annotated[PromptRepository, Depends(get_prompt_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> MarketPromptResp:
    shared_prompt = await shared_prompt_repo.find_by_id(shared_prompt_id)
    if shared_prompt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared prompt not found")

    title, description, content, tags_data = "", None, "", []
    author_name = ""

    if shared_prompt.prompt_id:
        prompt = await prompt_repo.get_by_id(shared_prompt.prompt_id)
        if prompt:
            title = prompt.title
            description = prompt.description
            content = prompt.content
            tags_data = list(prompt.tags)

    user = await user_repo.get_by_id(shared_prompt.user_id)
    if user:
        author_name = user.username

    is_liked = False
    is_favorited = False
    if current_user:
        like = await shared_prompt_repo.find_like(current_user.id, shared_prompt.id)
        is_liked = like is not None
        fav = await prompt_favorite_repo.find_by_user_and_shared_prompt(
            current_user.id, shared_prompt.id
        )
        is_favorited = fav is not None

    return MarketPromptResp.from_domain(
        shared_prompt,
        title=title,
        description=description,
        content=content,
        tags=tags_data,
        author_name=author_name,
        is_liked=is_liked,
        is_favorited=is_favorited,
    )


@market_router.post(
    "/market/prompts/{shared_prompt_id}/like",
    response_model=PromptLikeResp,
    status_code=status.HTTP_201_CREATED,
)
async def like_shared_prompt(
    shared_prompt_id: UUID,
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PromptLikeResp:
    shared_prompt = await handle_like_prompt(shared_prompt_id, current_user, shared_prompt_repo)
    return PromptLikeResp.from_domain(shared_prompt, message="Prompt liked successfully")


@market_router.delete(
    "/market/prompts/{shared_prompt_id}/like",
    response_model=PromptLikeResp,
    status_code=status.HTTP_200_OK,
)
async def unlike_shared_prompt(
    shared_prompt_id: UUID,
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PromptLikeResp:
    shared_prompt = await handle_unlike_prompt(shared_prompt_id, current_user, shared_prompt_repo)
    return PromptLikeResp.from_domain(shared_prompt, message="Prompt unliked successfully")


@market_router.post(
    "/market/prompts/{shared_prompt_id}/favorite",
    response_model=PromptFavoriteResp,
    status_code=status.HTTP_201_CREATED,
)
async def favorite_prompt(
    shared_prompt_id: UUID,
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    prompt_favorite_repo: Annotated[PromptFavoriteRepository, Depends(get_prompt_favorite_repo)],
    prompt_repo: Annotated[PromptRepository, Depends(get_prompt_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PromptFavoriteResp:
    favorite = await handle_favorite_prompt(
        shared_prompt_id,
        current_user,
        shared_prompt_repo,
        prompt_favorite_repo,
        prompt_repo,
        user_repo,
    )
    return PromptFavoriteResp.from_domain(favorite)


@market_router.delete("/market/prompts/{shared_prompt_id}/favorite", status_code=status.HTTP_200_OK)
async def unfavorite_prompt(
    shared_prompt_id: UUID,
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    prompt_favorite_repo: Annotated[PromptFavoriteRepository, Depends(get_prompt_favorite_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    await handle_unfavorite_prompt(
        shared_prompt_id, current_user, shared_prompt_repo, prompt_favorite_repo
    )
    return {"message": "ok"}


@market_router.get("/market/prompts/{shared_prompt_id}/export")
async def export_market_prompt(
    shared_prompt_id: UUID,
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    prompt_repo: Annotated[PromptRepository, Depends(get_prompt_repo)],
) -> Response:
    shared_prompt = await shared_prompt_repo.find_by_id(shared_prompt_id)
    if shared_prompt is None or shared_prompt.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared prompt not found")

    if not shared_prompt.prompt_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Original prompt no longer available"
        )

    prompt = await prompt_repo.get_by_id(shared_prompt.prompt_id)
    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Original prompt not found"
        )

    frontmatter: dict[str, object] = {"title": prompt.title}
    if prompt.description:
        frontmatter["description"] = prompt.description
    if prompt.tags:
        frontmatter["tags"] = prompt.tags
    frontmatter["version"] = prompt.version

    yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    markdown_str = f"---\n{yaml_str}---\n\n{prompt.content}"

    return Response(
        content=markdown_str,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=prompt.md"},
    )


@market_router.get(
    "/favorites/prompts", response_model=ListPromptFavoritesResp, status_code=status.HTTP_200_OK
)
async def list_prompt_favorites(
    prompt_favorite_repo: Annotated[PromptFavoriteRepository, Depends(get_prompt_favorite_repo)],
    prompt_repo: Annotated[PromptRepository, Depends(get_prompt_repo)],
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ListPromptFavoritesResp:
    favorites, total = await handle_list_prompt_favorites(
        current_user, prompt_favorite_repo, skip, limit
    )
    items: list[PromptFavoriteResp] = []
    for fav in favorites:
        version_info = await handle_check_favorite_version(fav, prompt_repo, shared_prompt_repo)
        items.append(PromptFavoriteResp.from_domain(fav, is_stale=version_info["is_stale"]))
    return ListPromptFavoritesResp(items=items, total=total)


@market_router.post(
    "/favorites/prompts/{favorite_id}/refresh",
    response_model=RefreshFavoriteResp,
    status_code=status.HTTP_200_OK,
)
async def refresh_prompt_favorite(
    favorite_id: UUID,
    prompt_favorite_repo: Annotated[PromptFavoriteRepository, Depends(get_prompt_favorite_repo)],
    prompt_repo: Annotated[PromptRepository, Depends(get_prompt_repo)],
    shared_prompt_repo: Annotated[SharedPromptRepository, Depends(get_shared_prompt_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RefreshFavoriteResp:
    favorite = await prompt_favorite_repo.find_by_id(favorite_id)
    if favorite is None or favorite.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")

    updated = await handle_refresh_favorite(
        favorite, prompt_repo, shared_prompt_repo, prompt_favorite_repo
    )
    return RefreshFavoriteResp(
        message="Favorite refreshed successfully",
        favorite=PromptFavoriteResp.from_domain(updated, is_stale=False),
    )


router = market_router
