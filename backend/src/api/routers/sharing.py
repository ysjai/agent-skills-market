from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.repositories import (
    SkillFavoriteRepository,
    get_category_repo,
    get_shared_skill_repo,
    get_skill_favorite_repo,
    get_skill_repo,
)
from src.api.schemas.shared_skill import ShareSkillReq, ShareSkillResp
from src.application.handlers.shared_skill_handlers import handle_share_skill, handle_unshare_skill
from src.domain.aggregates.user import User
from src.domain.repositories.category_repository import CategoryRepository
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository

router = APIRouter(prefix="/skills", tags=["sharing"])


@router.post(
    "/{skill_id}/share", response_model=ShareSkillResp, status_code=status.HTTP_201_CREATED
)
async def share_skill(
    skill_id: UUID,
    request: ShareSkillReq,
    skill_repo: Annotated[SkillRepository, Depends(get_skill_repo)],
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    category_repo: Annotated[CategoryRepository, Depends(get_category_repo)],
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ShareSkillResp:
    shared_skill = await handle_share_skill(
        skill_id=skill_id,
        user=current_user,
        category_id=request.category_id,
        share_message=request.share_message,
        skill_repo=skill_repo,
        shared_skill_repo=shared_skill_repo,
        category_repo=category_repo,
        favorite_repo=favorite_repo,
    )
    return ShareSkillResp.from_domain(shared_skill)


@router.delete("/{skill_id}/share", response_model=ShareSkillResp, status_code=status.HTTP_200_OK)
async def unshare_skill(
    skill_id: UUID,
    shared_skill_repo: Annotated[SharedSkillRepository, Depends(get_shared_skill_repo)],
    favorite_repo: Annotated[SkillFavoriteRepository, Depends(get_skill_favorite_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ShareSkillResp:
    shared_skill = await handle_unshare_skill(
        skill_id=skill_id,
        user=current_user,
        shared_skill_repo=shared_skill_repo,
        favorite_repo=favorite_repo,
    )
    return ShareSkillResp.from_domain(shared_skill)
