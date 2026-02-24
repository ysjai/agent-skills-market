# docs/templates/handler_create_skill.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.skill_repository import SkillRepository
from app.infra.persistence.db.session import get_db
from app.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository


async def get_skill_repo(
    db: AsyncSession = Depends(get_db),
) -> SkillRepository:
    return SqlSkillRepository(db)


import uuid

from app.domain.entities.skill import Skill

from app.domain.exceptions import SkillAlreadyExistsError
from app.domain.repositories.skill_repository import SkillRepository
from app.domain.value_objects.slug import Slug


async def handle_create_skill(
    user_id: uuid.UUID,
    name: str,
    description: str | None,
    skill_repo: SkillRepository,
) -> Skill:
    slug = Slug.from_name(name)

    existing = await skill_repo.get_by_slug(slug, user_id)
    if existing:
        raise SkillAlreadyExistsError(f"Skill with name '{name}' already exists")

    skill = Skill.create(
        user_id=user_id,
        name=name,
        description=description,
    )

    await skill_repo.save(skill)

    return skill



from app.dependencies.auth import get_current_user
from app.schemas.skill import CreateSkillReq, CreateSkillResp
from fastapi import APIRouter, Depends, status

from app.api.dependencies.repositories import get_skill_repo
from app.application.handlers.create_skill_handler import handle_create_skill
from app.domain.repositories.skill_repository import SkillRepository
from app.models.user import User

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post(
    "",
    response_model=CreateSkillResp,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    request: CreateSkillReq,
    skill_repo: SkillRepository = Depends(get_skill_repo),
    current_user: User = Depends(get_current_user),
) -> CreateSkillResp:
    skill = await handle_create_skill(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        skill_repo=skill_repo,
    )
    return CreateSkillResp.from_domain(skill)
