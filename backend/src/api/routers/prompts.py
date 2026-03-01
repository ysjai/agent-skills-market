from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.repositories import get_prompt_repo
from src.api.schemas.prompt import (
    CreatePromptReq,
    CreatePromptResp,
    GetPromptResp,
    ImportPromptReq,
    ListPromptsItemResp,
    ListPromptsResp,
    PromptVersionResp,
    UpdatePromptReq,
    UpdatePromptResp,
)
from src.application.handlers.create_prompt_handler import handle_create_prompt
from src.application.handlers.delete_prompt_handler import handle_delete_prompt
from src.application.handlers.export_prompt_handler import handle_export_prompt
from src.application.handlers.get_prompt_handler import handle_get_prompt
from src.application.handlers.get_prompt_version_handler import handle_get_prompt_version
from src.application.handlers.import_prompt_handler import handle_import_prompt
from src.application.handlers.list_prompt_versions_handler import handle_list_prompt_versions
from src.application.handlers.list_prompts_handler import handle_list_prompts
from src.application.handlers.publish_prompt_version_handler import handle_publish_prompt_version
from src.application.handlers.update_prompt_handler import handle_update_prompt
from src.domain.aggregates.user import User
from src.domain.repositories.prompt_repository import PromptRepository

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("", response_model=CreatePromptResp, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    request: CreatePromptReq,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> CreatePromptResp:
    prompt = await handle_create_prompt(
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        prompt_repo=prompt_repo,
        description=request.description,
        tags=request.tags,
    )
    return CreatePromptResp.from_domain(prompt)


@router.get("", response_model=ListPromptsResp)
async def list_prompts(
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    tag: str | None = Query(None),
    search: str | None = Query(None),
) -> ListPromptsResp:
    prompts, total = await handle_list_prompts(
        user_id=current_user.id,
        offset=offset,
        limit=limit,
        prompt_repo=prompt_repo,
        tag=tag,
        search=search,
    )
    items = [ListPromptsItemResp.from_domain(p) for p in prompts]
    return ListPromptsResp(items=items, total=total, offset=offset, limit=limit)


# IMPORTANT: /import MUST come before /{prompt_id} to avoid "import" matching as UUID
@router.post("/import", response_model=CreatePromptResp, status_code=status.HTTP_201_CREATED)
async def import_prompt(
    request: ImportPromptReq,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> CreatePromptResp:
    prompt = await handle_import_prompt(
        user_id=current_user.id,
        markdown_content=request.content,
        prompt_repo=prompt_repo,
    )
    return CreatePromptResp.from_domain(prompt)


@router.get("/{prompt_id}", response_model=GetPromptResp)
async def get_prompt(
    prompt_id: UUID,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> GetPromptResp:
    prompt = await handle_get_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id,
        prompt_repo=prompt_repo,
    )
    return GetPromptResp.from_domain(prompt)


@router.put("/{prompt_id}", response_model=UpdatePromptResp)
async def update_prompt(
    prompt_id: UUID,
    request: UpdatePromptReq,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> UpdatePromptResp:
    prompt = await handle_update_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id,
        prompt_repo=prompt_repo,
        title=request.title,
        content=request.content,
        description=request.description,
        tags=request.tags,
    )
    return UpdatePromptResp.from_domain(prompt)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: UUID,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> None:
    await handle_delete_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id,
        prompt_repo=prompt_repo,
    )


@router.post(
    "/{prompt_id}/versions", response_model=PromptVersionResp, status_code=status.HTTP_201_CREATED
)
async def publish_prompt_version(
    prompt_id: UUID,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> PromptVersionResp:
    version = await handle_publish_prompt_version(
        prompt_id=prompt_id,
        user_id=current_user.id,
        prompt_repo=prompt_repo,
    )
    return PromptVersionResp.from_domain(version)


@router.get("/{prompt_id}/versions", response_model=list[PromptVersionResp])
async def list_prompt_versions(
    prompt_id: UUID,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> list[PromptVersionResp]:
    versions = await handle_list_prompt_versions(
        prompt_id=prompt_id,
        user_id=current_user.id,
        prompt_repo=prompt_repo,
    )
    return [PromptVersionResp.from_domain(v) for v in versions]


@router.get("/{prompt_id}/versions/{version_id}", response_model=PromptVersionResp)
async def get_prompt_version(
    prompt_id: UUID,
    version_id: UUID,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> PromptVersionResp:
    version = await handle_get_prompt_version(
        prompt_id=prompt_id,
        version_id=version_id,
        user_id=current_user.id,
        prompt_repo=prompt_repo,
    )
    return PromptVersionResp.from_domain(version)


@router.get("/{prompt_id}/export")
async def export_prompt(
    prompt_id: UUID,
    prompt_repo: PromptRepository = Depends(get_prompt_repo),
    current_user: User = Depends(get_current_user),
) -> Response:
    markdown_str = await handle_export_prompt(
        prompt_id=prompt_id,
        user_id=current_user.id,
        prompt_repo=prompt_repo,
    )
    return Response(
        content=markdown_str,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=prompt.md"},
    )
