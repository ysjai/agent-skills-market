# docs/templates/dto_create_skill.py

import uuid
from datetime import datetime

from src.domain.entities.skill import Skill
from pydantic import BaseModel, Field


class CreateSkillReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Skill 名称")
    description: str | None = Field(None, max_length=2000, description="Skill 描述")


class CreateSkillResp(BaseModel):
    id: uuid.UUID = Field(..., description="Skill ID")
    name: str = Field(..., description="Skill 名称")
    slug: str = Field(..., description="Skill Slug")
    description: str | None = Field(None, description="Skill 描述")
    version: int = Field(..., description="版本号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    @classmethod
    def from_domain(cls, skill: Skill) -> CreateSkillResp:
        return cls(
            id=skill.id,
            name=skill.name,
            slug=str(skill.slug),
            description=skill.description,
            version=skill.version,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )


class ListSkillsItemResp(BaseModel):
    id: uuid.UUID = Field(..., description="Skill ID")
    name: str = Field(..., description="Skill 名称")
    slug: str = Field(..., description="Skill Slug")
    description: str | None = Field(None, description="Skill 描述")
    updated_at: datetime = Field(..., description="更新时间")

    @classmethod
    def from_domain(cls, skill: Skill) -> ListSkillsItemResp:
        return cls(
            id=skill.id,
            name=skill.name,
            slug=str(skill.slug),
            description=skill.description,
            updated_at=skill.updated_at,
        )
