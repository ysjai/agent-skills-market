from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.repositories import get_blob_repo, get_skill_repo, get_tree_repo
from app.api.schemas.skill import (
    CreateSkillReq,
    CreateSkillResp,
    GetSkillResp,
    ListSkillFilesResp,
    ListSkillsItemResp,
    UpdateSkillReq,
    UpdateSkillResp,
)
from app.application.handlers.create_skill_handler import handle_create_skill
from app.application.handlers.delete_skill_handler import handle_delete_skill
from app.application.handlers.download_skill_handler import handle_download_skill
from app.application.handlers.get_skill_handler import handle_get_skill
from app.application.handlers.get_tree_handler import handle_get_tree
from app.application.handlers.import_skill_handler import handle_import_skill
from app.application.handlers.list_skills_handler import handle_list_skills
from app.application.handlers.update_skill_handler import handle_update_skill
from app.domain.aggregates.user import User
from app.domain.repositories.blob_repository import BlobRepository
from app.domain.repositories.skill_repository import SkillRepository
from app.domain.repositories.tree_repository import TreeRepository

router = APIRouter(prefix="/skills", tags=["skills"])


ImportSkillReq = CreateSkillReq


class ListSkillsResp(BaseModel):
    items: list[ListSkillsItemResp]
    total: int


@router.post("", response_model=CreateSkillResp, status_code=status.HTTP_201_CREATED)
async def create_skill(
    request: CreateSkillReq,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    tree_repo: TreeRepository = Depends(get_tree_repo),
    current_user: User = Depends(get_current_user),
) -> CreateSkillResp:
    skill = await handle_create_skill(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
    )
    return CreateSkillResp.from_domain(skill)


@router.post("/import", response_model=CreateSkillResp, status_code=status.HTTP_201_CREATED)
async def import_skill(
    request: ImportSkillReq,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    tree_repo: TreeRepository = Depends(get_tree_repo),
    current_user: User = Depends(get_current_user),
) -> CreateSkillResp:
    skill = await handle_import_skill(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        slug=request.slug,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
    )
    return CreateSkillResp.from_domain(skill)


@router.get("", response_model=ListSkillsResp)
async def list_skills(
    skill_repo: SkillRepository = Depends(get_skill_repo),
    current_user: User = Depends(get_current_user),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> ListSkillsResp:
    skills = await handle_list_skills(
        user_id=current_user.id,
        offset=skip,
        limit=limit,
        skill_repo=skill_repo,
    )
    items = [ListSkillsItemResp.from_domain(s) for s in skills]
    return ListSkillsResp(items=items, total=len(items))


@router.get("/{skill_id}", response_model=GetSkillResp)
async def get_skill(
    skill_id: UUID,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    current_user: User = Depends(get_current_user),
) -> GetSkillResp:
    skill = await handle_get_skill(
        skill_id=skill_id,
        user_id=current_user.id,
        skill_repo=skill_repo,
    )
    return GetSkillResp.from_domain(skill)


@router.get("/{skill_id}/files", response_model=ListSkillFilesResp)
async def get_skill_files(
    skill_id: UUID,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    tree_repo: TreeRepository = Depends(get_tree_repo),
    current_user: User = Depends(get_current_user),
) -> ListSkillFilesResp:
    """Get list of files in a skill."""
    skill = await handle_get_skill(
        skill_id=skill_id,
        user_id=current_user.id,
        skill_repo=skill_repo,
    )
    if not skill.tree_id:
        return ListSkillFilesResp(skill_id=skill.id, skill_name=skill.name, files=[])
    tree = await handle_get_tree(tree_id=skill.tree_id, tree_repo=tree_repo)
    return ListSkillFilesResp.from_domain(skill, tree.entries)


@router.put("/{skill_id}", response_model=UpdateSkillResp)
async def update_skill(
    skill_id: UUID,
    request: UpdateSkillReq,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    current_user: User = Depends(get_current_user),
) -> UpdateSkillResp:
    skill = await handle_update_skill(
        skill_id=skill_id,
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        is_public=request.is_public,
        tree_id=request.tree_id,
        skill_repo=skill_repo,
    )
    return UpdateSkillResp.from_domain(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: UUID,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> None:
    await handle_delete_skill(
        skill_id=skill_id,
        user_id=current_user.id,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
    )


@router.get("/{skill_id}/download")
async def download_skill(
    skill_id: UUID,
    platform: str | None = Query(None),
    skill_repo: SkillRepository = Depends(get_skill_repo),
    tree_repo: TreeRepository = Depends(get_tree_repo),
    blob_repo: BlobRepository = Depends(get_blob_repo),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    content, media_type, filename = await handle_download_skill(
        user_id=current_user.id,
        skill_id=skill_id,
        platform=platform,
        skill_repo=skill_repo,
        tree_repo=tree_repo,
        blob_repo=blob_repo,
    )
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
