from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.user import User
from src.domain.exceptions import ResourceNotFoundError
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.user_repository import UserRepository


@dataclass
class MarketSkillData:
    id: UUID
    skill_id: UUID | None
    user_id: UUID
    category_id: UUID
    share_message: str | None
    like_count: int
    favorite_count: int
    status: str
    name: str
    description: str | None
    author_name: str
    is_liked: bool = False
    is_favorited: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MarketSkillListData:
    items: list[MarketSkillData] = field(default_factory=list)
    total: int = 0


class SkillFavoriteRepository(Protocol):
    async def find_by_user_and_shared_skill(
        self, user_id: UUID, shared_skill_id: UUID
    ) -> object | None: ...


async def handle_list_market_skills(
    keyword: str | None,
    category_id: UUID | None,
    sort_by: str,
    skip: int,
    limit: int,
    current_user: User | None,
    shared_skill_repo: SharedSkillRepository,
    favorite_repo: SkillFavoriteRepository | None = None,
    skill_repo: SkillRepository | None = None,
    user_repo: UserRepository | None = None,
) -> MarketSkillListData:
    shared_skills = await shared_skill_repo.find_active_by_filters(
        keyword=keyword,
        category_id=category_id,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )
    total = await shared_skill_repo.count_active_by_filters(
        keyword=keyword, category_id=category_id
    )

    items: list[MarketSkillData] = []
    for shared_skill in shared_skills:
        items.append(
            await _build_market_skill_resp(
                shared_skill=shared_skill,
                current_user=current_user,
                shared_skill_repo=shared_skill_repo,
                favorite_repo=favorite_repo,
                skill_repo=skill_repo,
                user_repo=user_repo,
            )
        )

    return MarketSkillListData(items=items, total=total)


async def handle_get_market_skill_detail(
    shared_skill_id: UUID,
    current_user: User | None,
    shared_skill_repo: SharedSkillRepository,
    favorite_repo: SkillFavoriteRepository | None = None,
    skill_repo: SkillRepository | None = None,
    user_repo: UserRepository | None = None,
) -> MarketSkillData:
    shared_skill = await shared_skill_repo.find_by_id(shared_skill_id)
    if shared_skill is None:
        raise ResourceNotFoundError("Shared skill not found")

    return await _build_market_skill_resp(
        shared_skill=shared_skill,
        current_user=current_user,
        shared_skill_repo=shared_skill_repo,
        favorite_repo=favorite_repo,
        skill_repo=skill_repo,
        user_repo=user_repo,
    )


async def _build_market_skill_resp(
    shared_skill: SharedSkill,
    current_user: User | None,
    shared_skill_repo: SharedSkillRepository,
    favorite_repo: SkillFavoriteRepository | None,
    skill_repo: SkillRepository | None = None,
    user_repo: UserRepository | None = None,
) -> MarketSkillData:
    # Resolve live data from Skill and User
    name = ""
    description: str | None = None
    author_name = ""

    if shared_skill.skill_id and skill_repo:
        skill = await skill_repo.get_by_id(shared_skill.skill_id)
        if skill:
            name = skill.name
            description = skill.description

    if user_repo:
        user_obj = await user_repo.get_by_id(shared_skill.user_id)
        if user_obj:
            author_name = user_obj.username

    if current_user is None:
        return _make_market_skill_data(shared_skill, name, description, author_name)

    like = await shared_skill_repo.find_like(current_user.id, shared_skill.id)
    is_favorited = await _find_favorite(
        favorite_repo=favorite_repo,
        user_id=current_user.id,
        shared_skill_id=shared_skill.id,
    )
    return _make_market_skill_data(
        shared_skill,
        name,
        description,
        author_name,
        is_liked=like is not None,
        is_favorited=is_favorited,
    )


def _make_market_skill_data(
    shared_skill: SharedSkill,
    name: str = "",
    description: str | None = None,
    author_name: str = "",
    is_liked: bool = False,
    is_favorited: bool = False,
) -> MarketSkillData:
    return MarketSkillData(
        id=shared_skill.id,
        skill_id=shared_skill.skill_id,
        user_id=shared_skill.user_id,
        category_id=shared_skill.category_id,
        share_message=shared_skill.share_message,
        like_count=shared_skill.like_count,
        favorite_count=shared_skill.favorite_count,
        status=shared_skill.status,
        name=name,
        description=description,
        author_name=author_name,
        is_liked=is_liked,
        is_favorited=is_favorited,
        created_at=shared_skill.created_at,
        updated_at=shared_skill.updated_at,
    )


async def _find_favorite(
    favorite_repo: SkillFavoriteRepository | None,
    user_id: UUID,
    shared_skill_id: UUID,
) -> bool:
    if favorite_repo is None:
        return False

    favorite = await favorite_repo.find_by_user_and_shared_skill(user_id, shared_skill_id)
    return favorite is not None
